import os
import json
import logging
import threading
from pathlib import Path
from BlueLLMTeam.utils.tqdm import trange_wrapper, tqdm, tqdm_wrapper

from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam import PromptDict as prompt


logger = logging.getLogger(__name__)


def create_file_structure(llm_endpoint: LLMEndpointBase) -> str:
    pm = prompt.file_system_lead()
    response = llm_endpoint.ask(pm)
    return response


def create_file_structure_employee(file_structure, llm_endpoint: LLMEndpointBase) -> str:
    file_creator = prompt.file_system_employee(file_structure)
    response = llm_endpoint.ask(file_creator)
    return response


def create_file_structure_enhance(file_structure, llm_endpoint: LLMEndpointBase) -> str:
    file_enhancer = prompt.file_system_enhancer(file_structure)
    response = llm_endpoint.ask(file_enhancer)
    return response


def create_file_structure_contents(file_structure, llm_endpoint: LLMEndpointBase, file) -> str:
    file_contents = prompt.file_contents_employee(file_structure, file)
    response = llm_endpoint.ask(file_contents)
    return response


def json_fs_to_file_paths(current_folder: str, fs: dict) -> list[str]:
    files = []
    for key, value in fs.items():
        folder = os.path.join(current_folder, key)
        if isinstance(value, dict):
            files.extend(json_fs_to_file_paths(folder, value))
        else:
            files.append(os.path.join(folder, value))
    return files


def generate_file_system(
        current_folder: str, 
        honey_context: str, 
        llm: LLMEndpointBase, 
        depth: int = 0, 
        max_depth: int = 5
):
    if depth >= max_depth:
        raise RecursionError(f"Failed to generate file system {depth} times")
    
    # Initial prompt and response
    pm_response = create_file_structure(llm)
    system_file = create_file_structure_enhance(pm_response, llm)
    #Range determines how complex and deep the system will generate file contents
    for _ in trange_wrapper(8, desc="Increasing filesystem complexity", leave=False):
        system_file = create_file_structure_enhance(system_file, llm)
    #Generate the json from the instructions given from the for loop.
    file_structure_response=create_file_structure_employee(system_file, llm)
    try:
        final_file_structure = json.loads(file_structure_response)
        # Convert JSON to list of files
        return json_fs_to_file_paths(current_folder, final_file_structure)
    except Exception as e:
        logger.error(f"Handle Conversation Error: {e}")
        return generate_file_system(
            current_folder=current_folder, 
            honey_context=honey_context, 
            llm=llm, 
            depth=depth + 1, 
            max_depth=max_depth
        )


def generate_file_content(
        file: str,
        local_fs: Path,
        file_structure: dict,
        llm: LLMEndpointBase,
        light_weight: bool = False
):
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
            contents = create_file_structure_contents(file_structure, llm, file)
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
) -> list[str]:
    """
    Create a file for the fake file system
    """
    # Remove possible duplicates
    files = set(files)

    # Build file structure
    file_structure = {}
    for file in files:
        parts = os.path.normpath(file).split(os.sep)
        sub_file_structure = file_structure
        for part in parts[:-1]:
            if part not in sub_file_structure:
                sub_file_structure[part] = {}
            sub_file_structure = sub_file_structure[part]
        sub_file_structure[parts[-1]] = ""

    # Wrapper function for file generation to update a progress bar
    def wrapper(pbar: tqdm, lock: threading.Lock, **kwargs):
        generate_file_content(**kwargs)
        with lock:
            pbar.update(1)

    # Create a lot of threads
    logger.info(f"Generating file contents for {len(files)} files")
    with tqdm_wrapper(total=len(files), desc="Generating file contents", leave=False) as pbar:
        lock = threading.Lock()
        threads: list[threading.Thread] = []
        for file in files:
            kwargs = {
                "pbar": pbar,
                "lock": lock,
                "file": file,
                "file_structure": file_structure,
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
