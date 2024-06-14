"""
Author: Mahesh Babu Kamepalli
Last Modified: Mahesh Babu Kamepalli

Context: This file is part of BlueLLMTeam to add content to some types of file

Feel free to add new type of files ass you need it
"""
from LLMEndpoint import ChatGPTEndpoint
import json
import os

# Load JSON data from a file
with open('data/companyinfo.json', 'r') as file:
    company_info = json.load(file)


class AddContents:
    def create_file_content(file_path):
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        # Get the file extension
        _, file_extension = os.path.splitext(file_path)

        # Determine the file type and create content accordingly
        if file_extension == '.java':
            #Add a prompt engineering code here abd update the result to the content
            content = "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n"
        elif file_extension == '.py':
            # Add a prompt engineering code here abd update the result to the content
            # Define the prompt_dict according to the required structure
            
            # Create an instance of ChatGPTEndpoint
            endpoint = ChatGPTEndpoint()
            
            # Get the response from the ChatGPT endpoint
            response = endpoint.ask(prompt_dict)
            
            if response:
                print("ChatGPT Response:", response.content)
            else:
                print("Failed to get response from ChatGPT.")

        elif file_extension == '.txt':
            # Add a prompt engineering code here abd update the result to the content
            content = "This is a sample text file."
        else:
            print(f"Unsupported file type: {file_extension}")
            return

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Content written to {file_path}")

AddContents().create_file_content("frank.py")