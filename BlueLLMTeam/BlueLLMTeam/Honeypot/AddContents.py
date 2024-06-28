"""
Author: Mahesh Babu Kamepalli
Last Modified: Simon Paulsson

Context: This file is part of BlueLLMTeam to add content to some types of file

Feel free to add new type of files ass you need it
"""

import os
import logging

from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam import PromptDict as prompt


logger = logging.getLogger(__name__)


def create_file_contents(file_path, llm_endpoint: LLMEndpointBase):
    # Get the file extension
    _, file_extension = os.path.splitext(file_path)

    if file_extension == '.py':
        return create_python_contents(file_path, llm_endpoint)
    elif file_extension == '.txt':
        return create_text_contents(file_path, llm_endpoint)
    elif file_extension == '.csv':
        return create_csv_contents(file_path, llm_endpoint)
    else:
        return create_misc_file_contents(file_path, llm_endpoint)


def create_python_contents(file_path: str, llm_endpoint: LLMEndpointBase) -> str:
    """
    Create realistic looking python contents for .py files
    """
    #Ask the advisor what they think the python file should be based on within the current directory.
    python_suggestion = prompt.python_advisor(file_path)
    advisor_response = llm_endpoint.ask(python_suggestion)
    #Gain insight from the advisor to produce the first set of code
    python_code = prompt.python_coder(advisor_response.content)
    python_code1 = llm_endpoint.ask(python_code)
    #Review itself to make sure the code looks correct and proper. Eliminate any keywords like fake data.
    python_review = prompt.python_reviewer(python_code1.content)
    file_response = llm_endpoint.ask(python_review)
    return file_response.content


def create_text_contents(file_path: str, llm_endpoint: LLMEndpointBase) -> str:
    """
    Create realistic looking text contents for .txt files
    """
    # Get advice from what we need to write in the text file based on the current working directory.
    text_suggestion = prompt.text_file_advisor(file_path)
    advisor_response = llm_endpoint.ask(text_suggestion)
    # Take the advice and provide a aseries of questions for the writer to write about.
    text_file = prompt.text_file_writer(advisor_response.content)
    file_response = llm_endpoint.ask(text_file)
    return file_response.content


def create_csv_contents(file_path: str, llm_endpoint: LLMEndpointBase) -> str:
    """
    Create realistic csv contents for .csv files
    """
    contents = ""
    csv_advisor = prompt.csv_advisor(file_path)
    csv_advisor_response = llm_endpoint.ask(csv_advisor)
    csv_header = prompt.csv_header(csv_advisor_response.content)
    csv_header_response = llm_endpoint.ask(csv_header)
    contents += csv_header_response.content
    
    csv_first_rows = prompt.csv_writer(csv_header_response.content)
    csv_first_rows_response = llm_endpoint.ask(csv_first_rows)
    contents += csv_first_rows_response.content
    x=0
    while x < 8:
        csv_append = prompt.csv_appender(csv_header_response.content, csv_first_rows_response.content)
        csv_append_response = llm_endpoint.ask(csv_append)
        contents += csv_append_response.content
        x+=1
    return contents


def create_misc_file_contents(file_path: str, llm_endpoint: LLMEndpointBase) -> str:
    """
    Create miscellaneous file contents
    """
    #Get advice from what we need to write in the text file based on the current working directory.
    text_suggestion = prompt.text_file_advisor(file_path)
    advisor_response = llm_endpoint.ask(text_suggestion)
    #Take the advice and provide a aseries of questions for the writer to write about.
    text_file = prompt.text_file_writer(advisor_response.content)
    file_response = llm_endpoint.ask(text_file)
    return file_response.content
