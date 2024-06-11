import os
import random
import string
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)

from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint

endpoint = ChatGPTEndpoint()


def create_random_text(length=10):
    """Generate random text of a given length."""
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))


def create_random_filesystem(base_dir, num_dirs=5, num_files_per_dir=5, file_size=10):
    """Create a randomized file system with directories and random text files."""
    os.makedirs(base_dir, exist_ok=True)
    
    for dir_num in range(num_dirs):
        dir_path = os.path.join(base_dir, f"dir_{dir_num}")
        os.makedirs(dir_path, exist_ok=True)
        
        for file_num in range(num_files_per_dir):
            file_path = os.path.join(dir_path, f"file_{file_num}.txt")
            create_random_file(file_path, file_size)


def generate_random_id(length=10):
    """Generate a random id of a given length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))




maxDepth = 2
maxContent = 2
maxFolders = 3
currentDepth = 0
base_directory = 'random_filesystem'


### Base prompt ###
systemRole = "You're a linux terminal that needs to provide a file system for a car manufacturing company."
user = "Linux developer"
context = "Filenames and file contents should be based on a car manufacturing company. The files should be files that you would find in an administrative file system of a car manufacturing company"
model = "gpt-3.5-turbo"


def create_random_file(file_path, file_name, folder_name, file_size=10):
    """Create a random text file with specified size."""
    # print(f"Creating file at {file_path}", file_path[file_path.find("/"):])
    try:
        with open(file_path, 'w') as file:
            file_prompt = {
                "systemRole": systemRole,
                "user": user,
                "context": context,
                "message": "For a file with the filename " + file_name + " that exists in a folder " + file_path[file_path.find("/"):] + " in a linux file system, write example contents without any explanatory text. I only want the content of the file with no other exxplanation or extra characters.",
                "model" : model
            }
            file_response = endpoint.ask(file_prompt)
            file.write(file_response.content)
    except Exception as e:
        print(f"Failed to create file at {file_path}. Error: {e}")


def generate_files(folders, current_path, depth):
    for i, folder in enumerate(folders):
        # print("Folder: ", folder)
        # print("Current depth: ", depth)
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
                        # os.makedirs(os.path.join(base_directory, folder, item[1:]), exist_ok=True)
                        # print("Subfolder: ", item)
                        generate_files([item[1:]], new_path, depth+1)
                    else:
                        # create_random_file(os.path.join(base_directory, folder, item))
                        create_random_file(os.path.join(new_path, item), item, folder)
                        # print("File: ", item)



# Usage

num_directories = 3
num_files_per_directory = 4
file_size_in_chars = 20

# create_random_filesystem(base_directory, num_directories, num_files_per_directory, file_size_in_chars)

# print(f"Randomized file system created at: {os.path.abspath(base_directory)}")

# response = endpoint.ask(root_directory_prompt)

# response_text = response.choices[0].message.content
    
# if response:
#     print("ChatGPT Response:", response)
#     print("Response text:", response.content)
# else:
#     print("Failed to get response from ChatGPT.")

root_dir_prompt = {
        "systemRole": systemRole,
        "user": user,
        "context": context,
        "message": "Give an exmaple of the base directory of a linux file system, without explanatory text, folder names only, one folder per line, without any special characters or numbers, just the names of the folders",
        "model" : model
    }

root_dir_response = endpoint.ask(root_dir_prompt)
root_folders = root_dir_response.content.split("\n")
print("Base folders: ", root_folders)

generate_files(root_folders, base_directory, 0)
