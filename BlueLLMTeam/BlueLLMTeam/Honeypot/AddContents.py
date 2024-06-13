"""
Author: Mahesh Babu Kamepalli
Last Modified: Mahesh Babu Kamepalli

Context: This file is part of BlueLLMTeam to add content to some types of file

Feel free to add new type of files ass you need it
"""

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
            #Add a prompt engineering code here abd update the result to the content
            content = "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n"
        elif file_extension == '.py':
            # Add a prompt engineering code here abd update the result to the content
            content = "def main():\n    print(\"Hello, World!\")\n\nif __name__ == '__main__':\n    main()\n"
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
