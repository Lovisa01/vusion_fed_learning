"""
Author: Franklin Parker 24/06/14
Purpose: Control prompt engineering methods to assign different system types, file respondents and more. Call the function in your main
python file where you want to use the JSON. 

Requirements: Heavily document the purpose of each JSON for example: 
Analytics agent specifically used in analyzing log files coming from the log file database. 
Python file content generator creating scripts during the file creation process for the honeypot.

"""

import json
from pathlib import Path

from BlueLLMTeam.utils.text import replace_tokens

data_folder = Path(__file__).parent.parent.parent / 'data'

with open(data_folder / 'companyinfo.json', 'r') as file:
    company_info = json.load(file)


#Python advisor interprets the data from the file path and the company information to determine the instructions to provide to the python engineering team.
def python_advisor(file_path):
    prompt_dict = {
        "systemRole": "You're a project leader for python file requirements. You need to review the code then provide feedback to the developer to make improvements. You know that these are company details but is not data to be used in the script." + str(company_info) + ". Make sure they create a real project and not just junk code. This is for a honeypot, but it's not meant to look like a honeypot.",
        "user": "Provide feedback on the code. Make sure to inform the developer to make calls to a fake db that houses company information. They should be calls to a MongoDB and then act like the code is working.",
        "context": str(company_info),
        "message": "Task: Write a great description for a python developer to create a file that works with mongo db to generate queries and create analysis on the information.\
        Step1: Analyse this folder structure: " + file_path + "\
        Step2: think about a python script based on the current context of the file directory provided in step1. For example if the file structure is volvo-cncmachinery it should have some kind of g-code interpret. If it's a human resource file it should call a fake db for human resources informatione etc...\
        Step3: Think about the design for a python script making and calling functions.\
        Step 4: Provide the instructions to the python developer.",
        "model" : "gpt-4o",
    }
    return (prompt_dict)

#Python coder acts on behalf of their manager. They take the instructions for creating the python file asked for by the advisor.
def python_coder(prompt):
    prompt_dict = {
        "systemRole": "You're a mid level python developer. You need to write a python script file. Based on the instructions given to you from the instructor",
        "user": "Senior Python developer working for a company as prompted from the system. Write a script based on the prompt given from the systems designer.",
        "context": "The company information is given here: " + str(company_info) + "\n",
        "message": "You must provide only code and here are the isntructions given by the designer:"  + prompt + " You may only provide python code nothing else. \n",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens":4096
    }
    return (prompt_dict)

#Team advisor for interpreting the information before coming up with a complete solution.
def python_reviewer(code):
    prompt_dict = {
        "systemRole": "You're a senior python developer. You need to optimize a python script file based on. Ensure the script is highly efficient.",
        "user": "You need to revise the existing python to replace any local host urls with the company name and wwww.[companyname]/ found in the company info provided. and then whatever makes sense so if it's mongo it should be rest service db, otherwise use common sense.",
        "context": "Comapny Information" + str(company_info) + "\n" ,
        "message": "Step 1 review the code:" + code + "\n\
                    Step2: Replace all code that says fake information with real information. For example you can use common admin as username and password would be super simple passwords that are extremely vulnerable.\n\
                    Step3: Ensure there's no company information directly enetered as jsons, it should be calling a mongo db. Generate and use an api_key variable using a guid. \n\
                    Step4: Write the code and only provide the code. Do not provide any additional text.\n",
        "model" : "gpt-3.5-turbo-0125",
    }
    return (prompt_dict)


#Text file advisor must understand based on the file path what they need to write the text file about.
def text_file_advisor(file_path):
    prompt_dict = {
        "systemRole": "You're in a company with the following background. Company info: " + str(company_info),
        "user": "Based on the company infomration and the file path you need to provide some reasoning for creating a text file. Ask yourself 10 questions to try and solve \
         what kind of information should go into this file. Remember you're an employee for this company creating a text file and all you have to go off is the file path. \n",
        "context": "File Path: " + file_path,
        "message": "Task: Provide a list of a minimum of 10 and a max of 20 questions to ask yourself about what information to write about. The questions need to be relevant to the current file path and company infomration.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)

#Text fie writer takes a response from the text file advisor.
def text_file_writer(questions):
    prompt_dict = {
        "systemRole": "You're in a company with the following background Your role is going to be based on the questions you're provided you must write a usefule text file. Company info: " + str(company_info),
        "user": "Based on the company infomration and questions provided you need to answer them as though you're working for the company as an employee expecting you to perform. \
         what kind of information should go into this file. Remember you're an employee for this company creating a text file and all you have to go off is the file path. \n",
        "context": "Questions provided: " + questions + "\n\n",
        "message": "Task: Provide a only the text to for the text file. Format the document, but do not provide the questions you're providing answers to just supply the answers neatly. Make at least 5 spelling errors along thew way. Author each file with super uncommon names from 2010.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)

#TEMPLATE - copy and paste this for easy prompt generation. Data structure used to create prompts.
def csv_advisor(file_path):
    prompt_dict = {
        "systemRole": "You're in a company with the following background Your role is going to be based on the questions you're provided you must provide instructions for what headers to write. Company info: " + str(company_info),
        "user": "Based on the company information and the file path you need to provide some reasoning for creating a text file. Ask yourself 10 questions to try and solve \
         what kind of information should go into this file. Remember you're an employee for this company creating a text file and all you have to go off is the file path. \n",
        "context": "File Path: " + file_path + "\n",
        "message":"Task: Provide a list of a minimum of 10 and a max of 20 questions to ask yourself about what information to write about. The questions need to be relevant to the current file path and company information.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)

#Writes the csv file headers
def csv_header(questions):
    prompt_dict = {
        "systemRole": "You are an essential employee who needs to provide a csv with only headers. Using the information give you should think about company information and text given to you. Company info: " + str(company_info),
        "user": "Based on the company information and the file path you need to provide some reasoning for creating a csv. \
         what kind of information should go into this file. Remember you're an employee for this company creating a text file and all you have to go off is the file path. \n",
        "context": "Questions: " + questions + "\n\n",
        "message":"Task: Write a csv file and only provide csv headers. Do not provide any other feedback. The csv only contains headers, but based on the context of the questions given, everything needs to relate to something quantifiable or extremely qualititative such as a rating or index. You don't need to list each column as a question. \n\
            Step1: Evaluate the information given from the questions segment. \n \
            Step2: Generate headers that make sense from the questions given with at least 5 columns up to 20. Headers for the csv should be expecting information below with short descriptions and mostly quantifiable data. For example # of [product] or quality rating of [product].\n \
            Step3: Provide the content in a comma separated value format. Do not comment, do not provide additional context afterwards, I only want csv formatted information.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)

#Writes the csv file contents for honeypot file content generation
def csv_writer(headers):
    prompt_dict = {
        "systemRole": "You are an essential employee who needs to add add records to a csv. Using the information give you should think about company information and text given to you. Company info: " + str(company_info),
        "user": "Based on company information and existing headers you need to continue adding additional records. \
         what kind of information should go into this file. Remember you're an employee for this company creating a text file and all you have to go off is the file path. \n",
        "context": "Headers: " + str(headers) + "\n\n",
        "message":"Task: return only headers in the csv, but everything needs to relate to something quantifiable or extremely qualititative such as a rating or index. You don't need to list each column as a question. \n\
            Step1: Evaluate the information given from the headers and company information. \n \
            Step2: Generate contents that make sense from the headers given rows should contain numbers and qualitative data such as ratings of good or bad, steer away from descriptions. \n \
            Step3: Return only csv rows which align with the provided headers. I want at least 20 rows. Do not comment, do not provide additional context afterwards, I only want csv formatted information.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)

#Writes the csv file contents for honeypot file content generation
def csv_appender(headers, previous_content):
    prompt_dict = {
        "systemRole": "You are an essential employee who needs to add add records to an existing csv. Using the information give you should think about company information and text given to you. Company info: " + str(company_info),
        "user": "Based on existing content please provide more csv records. \n",
        "context": "Headers: " + str(headers) + "\n\n\
                    Previous Content: " + previous_content,
        "message":"Task: provide rows for a csv, but everything needs to relate to something quantifiable or extremely qualititative such as a rating or index. \n\
            Step1: Evaluate the information given from the questions segment. \n \
            Step2: Generate rows that make sense from the provided 'Previous Content' and 'Headers' \n \
            Step3: Return only csv rows which align with the 'Headers' content given. DO NOT PROVIDE THE HEADERS AS YOUR RESPONSE. I want at least 20 rows.  Do not comment, do not provide additional context afterwards, I only want csv formatted information.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)


#TEMPLATE - copy and paste this for easy prompt generation. Data structure used to create prompts.
def generate_prompt():
    prompt_dict = {
        "systemRole": "You're a senior python developer. You need to optimize a python script file based on. Ensure the script is highly efficient.",
        "user": "Senior Python developer working for a company as prompted from the system.",
        "context": "context",
        "message": "Optimize a python script for this company to operate efficiently.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096
    }
    return (prompt_dict)


def file_system_creator(tokens: dict[str, str]) -> dict[str, str]:
    return {
        "systemRole": f"You are Linux expert at a company with the following information {company_info}. Please advise on the folder contents of the folders of a honeypot that is to be deployed to fool attackers. A folder should be prefixed with an # and all files should have an extension. You should only answer with one folder/file per line and nothing else.\n# Example output\n# private\n# public\nsecrets.txt",
        "user": "Expert Linux user at the company",
        "context": f"The current file system that you should implement is a honeypot with the following description:\n{tokens['HONEY_DESCRIPTION']}\nPlease give your answers with this in mind.",
        "message": f"What contents can be found in {tokens['PATH']}? Make sure to provide realistic examples that could fool a human attacker. Prefix ONLY folders with a #. Files are listed as is. Folders should not have an extension.",
        "model" : "gpt-3.5-turbo-0125",
    }


def linux_command_response(tokens: dict[str, str]) -> dict[str, str]:
    return {
        "systemRole": f"You are Linux expert at a company with the following information {company_info}. You know all linux commands and can give realistic outputs for any command you are presented with. ",
        "user": "Please provide a realistic output for the command you are presented with. Give no additional contents.",
        "context": "",
        "message": tokens['command'],
        "model" : "gpt-3.5-turbo-0125",
    }


def linux_important_files_creator(tokens: dict[str, str]) -> dict[str, str]:
    return {
        "systemRole": f"You are Linux expert at a company with the following information {company_info}. You know everything about how a the linux file system is built. ",
        "user": "Please provide realistic file contents for the file you are presented with. Give no additional contents.",
        "context": "",
        "message": tokens['file'],
        "model" : "gpt-3.5-turbo-0125",
    }


def cowrie_configuration_creator(tokens: dict[str, str]) -> dict[str, str]:
    return {
        "systemRole": f"You are cowrie honeypot expert at a company with the following information {company_info}. You know everything about Cowrie and how to best foul hackers.",
        "user": "Please provide realistic contents for the following configuration keys in cowrie. Please give your response as a JSON object with the keys at the top level.",
        "context": "",
        "message": tokens['keys'],
        "model" : "gpt-3.5-turbo-0125",
        "json_format": True,
    }
