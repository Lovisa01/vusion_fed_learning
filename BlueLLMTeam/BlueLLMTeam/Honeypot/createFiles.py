import os
import random
import string
from pathlib import Path
import threading

from BlueLLMTeam import PromptDict as prompt
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase, ChatGPTEndpoint
from BlueLLMTeam.Honeypot import AddContents 

def generate_random_id(length=10):
    """Generate a random id of a given length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def generate_file_contents(file_path):
    """Create a random text file."""
    try:
        AddContents.create_file_content(file_path)
    except Exception as e:
        print(f"Failed to create file at {file_path}. Error: {e}")


def generate_file_system(local_fs: Path, current_folder: str, honey_context: str, llm: LLMEndpointBase, depth: int = 0, max_depth: int = 5):
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
    if depth > max_depth:
        return
    
    tokens = {
        "HONEY_DESCRIPTION": honey_context,
        "PATH": current_folder,
    }
    prompt_dict = prompt.file_system_creator(tokens)
    response: str = llm.ask(prompt_dict).content

    folder_contents = response.split("\n")

    threads: list[threading.Thread] = []

    for folder_content in folder_contents:
        folder_content = folder_content.strip()

        # Ignore empty lines
        if not folder_content:
            continue

        if folder_content.startswith("#"):
            # Remove '#' from folder name
            folder_name = folder_content[1:].strip()

            # Create folder on local OS
            next_folder = os.path.join(current_folder, folder_name)
            local_path = local_fs / next_folder.lstrip("/")
            local_path.mkdir(parents=True)

            # Recursively add more folders in a new thread
            kwargs = {
                "local_fs" : local_fs,
                "current_folder" : next_folder,
                "honey_context" : honey_context,
                "llm" : llm,
                "depth" : depth + 1,
                "max_depth" : max_depth,
            }
            t = threading.Thread(target=generate_file_system, kwargs=kwargs)
            threads.append(t)
        else:
            file_path = os.path.join(current_folder, folder_content)
            local_file_path = local_fs / file_path.lstrip("/")

            # Temp solution
            # t = threading.Thread(target=local_file_path.touch)
            # Generate file contents
            kwargs = {
                "file_path": str(local_file_path),
                #"honey_context": honey_context,
                #"llm": llm,
            }
            t = threading.Thread(target=generate_file_contents, kwargs=kwargs)
            threads.append(t)
            
    # Spawn new threads
    for t in threads:
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()


if __name__ == "__main__":
    generate_file_system(Path("home"), "/home", "SSH honeypot with a python server", ChatGPTEndpoint())