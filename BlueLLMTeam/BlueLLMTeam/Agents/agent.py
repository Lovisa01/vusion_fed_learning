"""
Authors: Frank and Simon 
07/17/2024
"""

from BlueLLMTeam.LLMEndpoint import LLMEndpointBase, ChatGPTEndpoint
from BlueLLMTeam import PromptDict as prompt
import json
import os
from tqdm import trange

"""
FUNCTIONS
"""

llm_endpoint = ChatGPTEndpoint()

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


# Function to loop through directories and write contents back to the same file
def write_file_contents(base_path, llm_endpoint, file_structure):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:          
                with open(file_path, 'w') as output_file:
                    # Call the function to get contents from LLM
                    contents = create_file_structure_contents(file_structure, llm_endpoint, file)
                    # Call the function to write file contents
                    output_file.write(contents)
            except Exception as e:
                # Log the error if needed and continue
                pass  # Continue execution even if there's an error
                
# Function to create directories and files
def create_dirs_files(base_path, d):
    for key, value in d.items():
        path = os.path.join(base_path, key)
        try:
            if isinstance(value, dict):
                os.makedirs(path, exist_ok=True)
                create_dirs_files(path, value)
            else:
                dir_name = os.path.dirname(path)
                os.makedirs(dir_name, exist_ok=True)
                with open(path, 'w') as f:
                    f.write(value)
        except Exception as e:
            pass  # Continue execution even if there's an error



def handle_conversation(depth=5):
    if depth == 0:
        raise RecursionError
    
    # Initial prompt and response
    pm_response = create_file_structure(llm_endpoint)
    system_file = create_file_structure_enhance(pm_response,llm_endpoint)
    #Range determines how complex and deep the system will generate file contents
    for _ in trange(8):
        system_file = create_file_structure_enhance(system_file,llm_endpoint)
    #Generate the json from the instructions given from the for loop.
    file_structure_response=create_file_structure_employee(system_file,llm_endpoint)
    try:
        final_file_structure = json.loads(file_structure_response)
        return final_file_structure
    except Exception as e:
        print(f"Handle Conversation Error: {e}")
        return handle_conversation(depth -1)
        

"""
Logic
"""

# Determine the base directory based on the location of the script
base_dir = os.path.dirname(os.path.abspath(__file__))
# Define the relative path to the target directory
relative_path = os.path.join(base_dir, '..', 'Honeypot', 'tmpfs')
# Ensure the relative path is absolute
absolute_relative_path = os.path.abspath(relative_path)

# Creates the LLM generated JSON to pass to the create directory function.
company_files = handle_conversation()
# Create directories and files at the specified relative path
create_dirs_files(absolute_relative_path, company_files)
#Generates comtents within each file (optional heavy duty)
write_file_contents(relative_path, llm_endpoint, company_files)