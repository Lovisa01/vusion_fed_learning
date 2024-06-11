import os
import random
import string
import sys
# Don't know if this is the right way to do this but its to be able to import LLMEndpoint from the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint

endpoint = ChatGPTEndpoint()

## Global variables to control the file system generation
maxDepth = 2
maxContent = 2
maxFolders = 3
base_directory = 'random_filesystem'


### Base prompt ###
systemRole = "You're a linux terminal that needs to provide a file system for a car manufacturing company."
user = "Linux developer"
context = "Filenames and file contents should be based on a car manufacturing company. The files should be files that you would find in an administrative file system of a car manufacturing company"
model = "gpt-3.5-turbo"


def create_random_file(file_path, file_name, folder_name):
    """Create a random text file."""
    try:
        with open(file_path, 'w') as file:
            file_prompt = {
                "systemRole": systemRole,
                "user": user,
                "context": context,
                "message": "For a file with the filename " + file_name + " that exists in a folder " + file_path[file_path.find("/"):] + #this used the entire folder path except base directory, might want to use folder_name ? maybe not? (refine later)
                 " in a linux file system, write example contents without any explanatory text. I only want the content of the file with no other exxplanation or extra characters.",
                "model" : model
            }
            file_response = endpoint.ask(file_prompt)
            file.write(file_response.content)
    except Exception as e:
        print(f"Failed to create file at {file_path}. Error: {e}")


def generate_files(folders, current_path, depth):
    for i, folder in enumerate(folders):
        if depth < maxDepth and i < maxFolders:
            new_path = os.path.join(current_path, folder)
            os.makedirs(new_path, exist_ok=True)
            folder_prompt = {
                "systemRole": systemRole,
                "user": user,
                "context": context,
                "message": "Give an example directory listing for the folder " + folder + " in a linux file system, file names and folder names only, one per line, without explanatory text, where subfolders are prefixed with #. Do not use placeholder names, give everything a name that is related to the company or the industry.",
                "model" : model
            }
            folder_response = endpoint.ask(folder_prompt)
            content = folder_response.content.split("\n")

            for index, item in enumerate(content):
                if index <= maxContent:
                    if item.startswith("#"):
                        generate_files([item[1:]], new_path, depth+1)
                    else:
                        create_random_file(os.path.join(new_path, item), item, folder)

# Prompt for the root directory of the file system
root_dir_prompt = {
        "systemRole": systemRole,
        "user": user,
        "context": context,
        "message": "Give an exmaple of the base directory of a linux file system, without explanatory text, folder names only, one folder per line, without any special characters or numbers, just the names of the folders",
        "model" : model
    }

root_dir_response = endpoint.ask(root_dir_prompt)
root_folders = root_dir_response.content.split("\n")

generate_files(root_folders, base_directory, 0)
