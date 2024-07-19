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
        "max_tokens": 4096,
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
            Step1:  the information given from the questions segment. \n \
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
            Step1:  the information given from the headers and company information. \n \
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
            Step1:  the information given from the questions segment. \n \
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

#File system lead initiial conversation
def file_system_lead():
    prompt_dict = {
        "systemRole": "You're a project manager. Your job is to ensure the creation of a robust file system for the following company information. \n \n Copmany Info:" + str(company_info) + "\n\n \
            Provide an interpreatable file structure that a coder will be able to look at and turn into python code to create the files.",
        "user": "You're a project manager. Your job is to ensure the creation of a robust file system for the following company information. \n \n Company Info:" + str(company_info) + "\n\n",
        "context": "Research the size of that company then make sure the size of the company has an appropriate folder and file structure. If it's 100 or less it may only need 20 folders, but if it's much larger it's going to need at least 50 folders. Provide files as well. ",
        "message": "Task: Create an initial scope of what files and folders need to be included. Write out what needs to happen in a detailed line item. Include the file names and folders. Make sure it makes sense for a real company. Do not use obvious names. Research the company and put relevant information. Do not put normal entries. Example output: -Primary Folder \n  -SubFolder \n -Subfolder \n         -Subfolder. Take your time \n Step2: Outline that at least one folder needs to contain a website with a unique folder name for the website such as the company name and some randomly generated cool name. Outline the website project and what files and configurations need to be included. The website should be based around node js. Make sure all regions include files for specific cities, states, counties, or prefectures rather than an entire geograpic region. List very specific places. Do not just provide africa, asia etc...",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096,
        "json_format":False,
    }
    return (prompt_dict)

#File system lead initiial conversation
def file_system_enhancer(file_structure):
    prompt_dict = {
        "systemRole": "You are a file system architect. You need to revise the file and folder structure you've been given. Research the following company:  \n \n Company Info:" + str(company_info) + "\n\n \
            Provide an interpreatable file structure that a coder will be able to look at and turn into python code to create the files.",
        "user": "You need to send back a more robust file system with a deeply nested network system with a large variety of files. Create file and folder structures for websites, cost estimates, customer information, employee information, and anything with highly sensitive information.",
        "context": "Research the size of that company then make sure the size of the company has an appropriate folder and file structure. If it's 100 or less it may only need 20 folders, but if it's much larger it's going to need at least 50 folders. Provide files as well. Here's the previous file structure, if blank then this is the initial startup the file structure \n File Structure:" + str(file_structure),
        "message": "Task: Enhance the file system you were given with the context provided earlier. Make sure to provide extremely sensitive looking information. Take your time to think before answering. \n \n Step 1: Review the existing content of the folder structure \n \n Step 2: Make sure no files or folders are labeled obvious names including sensitive information. Step 3: Do not use generic names for anything. Replace file names that say iteration, employee 1, server_config, customer, project, and replace them with names the company may use. Make up fake names using names from existing projects from history. Use historical names for employees. INCLUDE FILES THAT WILL HAVE SOCIAL SECURITY NUMBERS IN THEM \n\n Step 4: For any websites add in javascript and node js server configs. Step 5: Ensure file names do not include numerical orders, they should be dates if anything. Also do not generate folders with generic names like a or b. Use a name generator to think more creatively like project. Ensure folder and file names are using specific cities, counties, states, countries, but not too broad of regions. Avoid saying Europe, Africa, USA by themselves.  \n \n Step 6: Increase the complexity and add new and more in depth levels to the file and folder structure. \n",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096,
        "json_format":False,
    }
    return (prompt_dict)

#File system lead conversation and internal dialogue.
def file_system_employee(file_structure):
    schema = """
{
    "top_folder": {
        "subfolder_1": {
            "subfolder_1_1": {
                "file_1": "",
                "file_2": "",
                "subfolder_1_1_1": {
                    "file_1": "",
                    "file_2": ""
                }
            }
        },
        "subfolder_2": {
            "subfolder_2_1": {
                "file_1": "",
                "file_2": "",
                "file_3": "",
                "subfolder_2_1_1": {
                    "file_1": "",
                    "file_2": ""
                }
            },
            "subfolder_2_2": {
                "file_1": "",
                "subfolder_2_2_1": {
                    "file_1": "",
                    "file_2": ""
                },
                "file_2": "",
                "subfolder_2_2_2": {
                    "file_1": "",
                    "file_2": "",
                    "file_3": ""
                }
            }
        },
        "subfolder_3": {
            "subfolder_3_1": {
                "file_1": "",
                "subfolder_3_1_1": {
                    "file_1": "",
                    "file_2": ""
                }
            },
            "subfolder_3_2": {
                "file_1": "",
                "file_2": "",
                "subfolder_3_2_1": {
                    "file_1": "",
                    "file_2": ""
                }
            },
            "subfolder_3_3": {
                "file_1": "",
                "file_2": "",
                "subfolder_3_3_1": {
                    "file_1": "",
                    "file_2": ""
                }
            }
        },
        "file_1": "",
        "file_2": ""
    }
}
"""

    prompt_dict = {
        "systemRole": "You've just been hired by the following compnay: \n \n Copmany Info:" + str(company_info) + "\n\n " + "The file structure is: " + str(file_structure),
        "user": "You have been given a file structure from your boss you need to generate the python code to create all the folders and it's subfolders.",
        "context": "Make sure to also create the files as well.",
        "message": "You will provide a json, make sure all files have extensions. Provide only a json in this format: ' " + schema,
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096,
        "json_format":True,
    }
    return (prompt_dict)

#File system lead conversation and internal dialogue.
def file_contents_employee(file_structure, file):
    
    prompt_dict = {
        "systemRole": "You've just been hired by the following compnay: \n \n Copmany Info:" + str(company_info) + "\n\n " + "The file structure is: " + str(file_structure),
        "user": "You have been given a file and a file structure. File: " + str(file) + "\n \n Here's the file structure: " + str(file_structure),
        "context": "Generate useful content for the file. Do not use generic naming. Do not say meeting_1. Use names from different countries. Make the contents unique. Ensuer the file contents are thorough. \n",
        "message": "Provide only the file contents. If the file is a png, jpg or image file type then return an image based on the file name and where it exists in the structure. Otherwise generate appropriate content. Only return file contents no comments or anything else. \n \n Task: Generate file contents following the guidelines given. \n \n Step 1: Evaluate the file name. Step 2: Look at the file extension so .xlsx or .docx whatever the file extension is and use that to determine the file format based off the of the extension. \n Step 3: Look and see where in the file structure it resides. \n Step 4: Think hard about the information you might find in a company's file. Provide client specific information. Do not space general regions state exact cities in those regions. Do not use plenty of jargon. Any files with employee information should contain social security numbers in the format of xxx-xx-xxxx. \n Step 5: Review the content think hard. Use historical names. If mentioning places, mention real places. No finances or revenue should be a perfect number, it should have odd values. If it's expenses provide the name of real companies and places along with the items purchased and the cost. In the websites, make sure to provide robust website programming using cards and more. \n Step 5: Review the files and ensure no 12345 numbers are being used. Make sure to include fake social security numbers for employee documents in the format of ###-##-####.  \n Step 6: Write the contents provide nothing else beyond that.",
        "model" : "gpt-3.5-turbo-0125",
        "max_tokens": 4096,
        "json_format":False,
    }
    return (prompt_dict)



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
        "message": "\n".join(f"{key}: Example: {value}" for key, value in tokens['keys'].items()),
        "model" : "gpt-3.5-turbo-0125",
        "json_format": True,
    }
