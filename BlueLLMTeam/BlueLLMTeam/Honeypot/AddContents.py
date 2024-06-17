"""
Author: Mahesh Babu Kamepalli
Last Modified: Mahesh Babu Kamepalli

Context: This file is part of BlueLLMTeam to add content to some types of file

Feel free to add new type of files ass you need it
"""
from LLMEndpoint import ChatGPTEndpoint
import json
import os

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
            try:
                with open(file_path, 'w') as file:
                    prompt = {
                        "systemRole": "You are a Text genrator",
                        "user": "user",
                        "context": "I am a bread company",
                        "message": "Give me a java code without any explanation",
                        "model": "gpt-3.5-turbo"
                    }
                    file_response = llm_endpoint.ask(prompt)
                    print(file_response)
                    file.write(file_response.content)
            except Exception as e:
                print(f"Failed to add content to the file at {file_path}. Error: {e}")
        elif file_extension == '.py':
            # Add a prompt engineering code here abd update the result to the content
            content = "def main():\n    print(\"Hello, World!\")\n\nif __name__ == '__main__':\n    main()\n"
        elif file_extension == '.txt':
            try:
                with open(file_path, 'w') as file:
                    prompt = {
                        "systemRole": "You are a Text genrator",
                        "user": "user",
                        "context": "I am a bread company",
                        "message": "Give me some text data without any explanation",
                        "model": "gpt-3.5-turbo"
                    }
                    file_response = llm_endpoint.ask(prompt)
                    print(file_response)
                    file.write(file_response.content)
            except Exception as e:
                print(f"Failed to add content to the file at {file_path}. Error: {e}")
        elif file_extension == '.c':
            try:
                with open(file_path, 'w') as file:
                    prompt = {
                        "systemRole": "You are a Text genrator",
                        "user": "user",
                        "context": "I am a bread company",
                        "message": "Give me a c code without any explanation",
                        "model": "gpt-3.5-turbo"
                    }
                    file_response = llm_endpoint.ask(prompt)
                    print(file_response)
                    file.write(file_response.content)
            except Exception as e:
                print(f"Failed to add content to the file at {file_path}. Error: {e}")
        else:
            print(f"Unsupported file type: {file_extension}")
            return

