import os
import random
import string
import sys


def generate_random_id(length=10):
    """Generate a random id of a given length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def create_random_file(file_path, file_name, folder_name, prompt_dict: dict[str, str], llm_endpoint):
    """Create a random text file."""
    try:
        with open(file_path, 'w') as file:
            file_prompt = {
                "systemRole": prompt_dict["systemRole"],
                "user": prompt_dict["user"],
                "context": prompt_dict["context"],
                "message": "For a file with the filename " + file_name + " that exists in a folder " + file_path[file_path.find("/"):] + #this used the entire folder path except base directory, might want to use folder_name ? maybe not? (refine later)
                 " in a linux file system, write example contents without any explanatory text. I only want the content of the file with no other exxplanation or extra characters.",
                "model" : prompt_dict["model"]
            }
            file_response = llm_endpoint.ask(file_prompt)
            file.write(file_response.content)
    except Exception as e:
        print(f"Failed to create file at {file_path}. Error: {e}")


def generate_files(folders, current_path, depth, maxDepth, maxContent, maxFolders, prompt_dict: dict[str, str], llm_endpoint):
    for i, folder in enumerate(folders):
        if depth < maxDepth and i < maxFolders:
            new_path = os.path.join(current_path, folder)
            os.makedirs(new_path, exist_ok=True)
            folder_prompt = {
                "systemRole": prompt_dict["systemRole"],
                "user": prompt_dict["user"],
                "context": prompt_dict["context"],
                "message": "Give an example directory listing for the folder " + folder + " in a linux file system, file names and folder names only, one per line, without explanatory text, where subfolders are prefixed with #. Do not use placeholder names, give everything a name that is related to the company or the industry.",
                "model" : prompt_dict["model"]
            }
            folder_response = llm_endpoint.ask(folder_prompt)
            content = folder_response.content.split("\n")

            for index, item in enumerate(content):
                if index <= maxContent:
                    if item.startswith("#"):
                        generate_files([item[1:]], new_path, depth+1, maxDepth, maxContent, maxFolders, prompt_dict, llm_endpoint)
                    else:
                        create_random_file(os.path.join(new_path, item), item, folder, prompt_dict, llm_endpoint)

