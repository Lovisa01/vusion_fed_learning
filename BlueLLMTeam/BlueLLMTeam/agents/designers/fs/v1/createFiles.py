import os
from pathlib import Path
import threading
import logging
from BlueLLMTeam.utils.tqdm import tqdm_wrapper, tqdm

from BlueLLMTeam import PromptDict as prompt
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase, ChatGPTEndpoint
from . import AddContents
from BlueLLMTeam.utils.threading import ThreadWithReturnValue


logger = logging.getLogger(__name__)


def generate_file_content(file: str, local_fs: Path, llm: LLMEndpointBase, light_weight: bool = False):
    """
    Generate file contents and add them to a file on the system

    Arguments:
        file: File path of the file
        local_fs: Path to the local directory to store the file under
        llm: LLM endpoint to send the request to
        light_weight: No generation with LLM, add only the text "\n" to each file
    """
    local_file_path = local_fs / file.lstrip("/")
    
    # Generate file contents
    if light_weight:
        contents = "\n"
    else:
        try:
            contents = AddContents.create_file_contents(file, llm)
        except Exception as e:
            logger.warning(f"Failed to generate file contents for {file}. Error: {e}")
            contents = "\n"

    # Write contents to the file
    try:
        local_file_path.parent.mkdir(exist_ok=True, parents=True)
        local_file_path.write_text(contents)
    except Exception as e:
        logger.warning(f"Failed to write file contents for {local_file_path}. Error: {e}")
        return


def generate_file_contents(
        local_fs: Path,
        files: list[str],
        honey_context: str,
        llm: LLMEndpointBase,
        light_weight: bool = False,
    ):
    """
    Create a file for the fake file system
    """
    # Remove possible duplicates
    files = set(files)

    # Wrapper function for file generation to update a progress bar
    def wrapper(pbar: tqdm, lock: threading.Lock, **kwargs):
        generate_file_content(**kwargs)
        with lock:
            pbar.update(1)

    # Create a lot of threads
    with tqdm_wrapper(total=len(files), desc="Generating file contents", leave=False) as pbar:
        lock = threading.Lock()
        threads: list[threading.Thread] = []
        for file in files:
            kwargs = {
                "pbar": pbar,
                "lock": lock,
                "file": file,
                "local_fs": local_fs,
                "llm": llm,
                "light_weight": light_weight,
            }
            t = threading.Thread(target=wrapper, kwargs=kwargs)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()


def generate_file_system(
        current_folder: str, 
        honey_context: str, 
        llm: LLMEndpointBase, 
        depth: int = 0, 
        max_depth: int = 5
    ) -> list[str]:
    """
    Generate a file system recursively. 
    
    From the 'current_folder' generate subfolders and files. 
    Recursively generate more contents in the subfolders and
    generate contents for the files with an LLM.

    Break at a maximum depth to stop to deep filesystems

    Args:
        local_fs: path to the local storage of the filesystem
        current_folder: current folder to generate contents for
        honey_context: the context for the filesystem
        llm: the LLM endpoint to use for prompting
        depth: current depth
        max_depth: maximum depth, break if this is exceeded
    """
    folder_contents: list[str] = []
    if depth > max_depth:
        return folder_contents
    
    tokens = {
        "HONEY_DESCRIPTION": honey_context,
        "PATH": current_folder,
    }
    prompt_dict = prompt.file_system_creator(tokens)
    response: str = llm.ask(prompt_dict)

    new_folder_contents = response.split("\n")

    threads: list[ThreadWithReturnValue] = []

    for folder_content in new_folder_contents:
        folder_content = folder_content.strip()

        # Ignore empty lines
        if not folder_content:
            continue

        if folder_content.startswith("#"):
            # Remove '#' from folder name
            folder_name = folder_content[1:].strip()
            next_folder = os.path.join(current_folder, folder_name)

            # Recursively add more folders in a new thread
            kwargs = {
                "current_folder" : next_folder,
                "honey_context" : honey_context,
                "llm" : llm,
                "depth" : depth + 1,
                "max_depth" : max_depth,
            }
            t = ThreadWithReturnValue(target=generate_file_system, kwargs=kwargs)
            threads.append(t)
        else:
            # Add the file to the contents of this folder
            folder_contents.append(os.path.join(current_folder, folder_content.strip()))
            
            
    # Spawn new threads
    for t in threads:
        t.start()
    
    # Wait for all threads to complete and extend the folder contents
    sub_contents = []
    for t in threads:
        contents = t.join()
        if contents is not None:
            sub_contents.extend(contents)
    
    folder_contents.extend(sub_contents)
    return folder_contents


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    llm = ChatGPTEndpoint()
    files = generate_file_system("/home", "SSH honeypot with a python server", llm, max_depth=2)
    generate_file_contents(Path("tmp"), files, "", llm, light_weight=False)
