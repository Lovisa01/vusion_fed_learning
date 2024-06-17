"""
Author: Franklin Parker 24/06/14
Purpose: Control prompt engineering methods to assign different system types, file respondents and more. Call the function in your main
python file where you want to use the JSON. 

Requirements: Heavily document the purpose of each JSON for example: 
Analytics agent specifically used in analyzing log files coming from the log file database. 
Python file content generator creating scripts during the file creation process for the honeypot.

"""


from abc import ABC, abstractmethod
import json
from pathlib import Path

data_folder = Path(__file__).parent.parent.parent / 'data'

with open(data_folder / 'companyinfo.json', 'r') as file:
    company_info = json.load(file)

class AbstractPromptGenerator(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def generate_prompt(self):
        pass

class PromptGenerator(AbstractPromptGenerator):

    def python_coder(self):
        prompt_dict = {
            "systemRole": "You're a senior python developer. You need to write a python script file based on " + str(company_info) + ". Ensure the script is highly efficient.",
            "user": "Senior Python developer working for a company as prompted from the system. Write a script using the file path as the context for the script. Also think about the compnay info. File Path:" + self.file_path + "Task: Provide only code do not provide any additional text, I just want code. Step 1: think about what type of script you might run based on the file path. Step2: Write the code with comments added.",
            "context": str(company_info),
            "message": "Task: Write a ptyhon script for the particular project. You know that the project should be based on the company information.\
                Step1: Analyse this folder structure: " + self.file_path + "\
                    Step2: think about a python script based on the current context of the file directory provided in step1\
                        Step3: Make this a very convincing python script where it creates functions.\
                                Step 4: provide the code in an easy way for me to parse out so don't write python at the top just provide a string of all the code",
            "model" : "gpt-3.5-turbo",
        }
        return (prompt_dict)
    
    def generate_prompt(self):
        prompt_dict = {
            "systemRole": "You're a senior python developer. You need to optimize a python script file based on " + self + ". Ensure the script is highly efficient.",
            "user": "Senior Python developer working for a company as prompted from the system.",
            "context": self,
            "message": "Optimize a python script for this company to operate efficiently.",
            "model" : "gpt-3.5-turbo",
        }
        return (prompt_dict)


#EXAMPLE USAGE
#prompt_gen = PromptGenerator(file_path="/bakery/finances/fiscalreport")
#general_prompt = prompt_gen.python_coder()
#print(general_prompt)