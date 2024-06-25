"""
Author: Mahesh Babu Kamepalli
Last Modified: Mahesh Babu Kamepalli

Context: This file is part of BlueLLMTeam to add content to some types of file

Feel free to add new type of files ass you need it
"""

import os
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam import PromptDict as prompt


llm_endpoint = ChatGPTEndpoint()


def create_file_content(file_path):
    print("the file path is here:")
    print(file_path)
    # Get the file extension
    _, file_extension = os.path.splitext(file_path)

    #WRITE TO A PYTHON FILE
    if file_extension == '.py':
        try:
            with open(file_path, 'w') as file:
                #Ask the advisor what they think the python file should be based on within the current directory.
                python_suggestion = prompt.python_advisor(file_path)
                print(python_suggestion)
                advisor_response = llm_endpoint.ask(python_suggestion)
                #Gain insight from the advisor to produce the first set of code
                python_code = prompt.python_coder(advisor_response.content)
                python_code1 = llm_endpoint.ask(python_code)
                #Review itself to make sure the code looks correct and proper. Eliminate any keywords like fake data.
                python_review = prompt.python_reviewer(python_code1.content)
                file_response = llm_endpoint.ask(python_review)
                file.write(file_response.content)
        except Exception as e:
            print(f"Failed to add content to the file at {file_path}. Error: {e}")

    #WRITE TO A TEXT FILE
    elif file_extension == '.txt':
        try:
            with open(file_path, 'w') as file:
                #Get advice from what we need to write in the text file based on the current working directory.
                text_suggestion = prompt.text_file_advisor(file_path)
                advisor_response = llm_endpoint.ask(text_suggestion)
                #Take the advice and provide a aseries of questions for the writer to write about.
                text_file = prompt.text_file_writer(advisor_response.content)
                file_response = llm_endpoint.ask(text_file)
                file.write(file_response.content)
        except Exception as e:
            print(f"Failed to add content to the file at {file_path}. Error: {e}")
    
    #Write to a CSV file
    elif file_extension == '.csv':
        try:
            with open(file_path, 'w') as file:
                        csv_advisor = prompt.csv_advisor(file_path)
                        csv_advisor_response = llm_endpoint.ask(csv_advisor)
                        csv_header = prompt.csv_header(csv_advisor_response.content)
                        csv_header_response = llm_endpoint.ask(csv_header)
                        file.write(csv_header_response.content)
            with open(file_path, 'a') as file:
                csv_first_rows = prompt.csv_writer(csv_header_response.content)
                csv_first_rows_response = llm_endpoint.ask(csv_first_rows)
                file.write(csv_first_rows_response.content)
                x=0
                while x <20: 
                    csv_append = prompt.csv_appender(csv_header_response.content, csv_first_rows_response.content)
                    csv_append_response = llm_endpoint.ask(csv_append)
                    file.write(csv_append_response.content)
                    x+=1
        except Exception as e:
            print(f"Failed to add content to the file at {file_path}. Error: {e}")
    else:
        try:
            with open(file_path, 'w') as file:
                #Get advice from what we need to write in the text file based on the current working directory.
                text_suggestion = prompt.text_file_advisor(file_path)
                advisor_response = llm_endpoint.ask(text_suggestion)
                #Take the advice and provide a aseries of questions for the writer to write about.
                text_file = prompt.text_file_writer(advisor_response.content)
                file_response = llm_endpoint.ask(text_file)
                file.write(file_response.content)
        except Exception as e:
            print(f"Failed to add content to the file at {file_path}. Error: {e}")


