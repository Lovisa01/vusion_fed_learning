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
            "context": str(company_info),
            "message": "You must provide only code and here are the isntructions given by the designer:"  + prompt + " You may only provide python code nothing else.",
            "model" : "gpt-3.5-turbo-0125",
            "max_tokens":4096
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
        }
        return (prompt_dict)

