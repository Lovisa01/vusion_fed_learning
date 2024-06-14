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


class AbstractPromptGenerator(ABC):
    def __init__(self, company_info):
        self.company_info = company_info

    @abstractmethod
    def generate_prompt(self):
        pass

    def export_json(self, prompt_dict):
        return json.dumps(prompt_dict, indent=4)

class PromptGenerator1(AbstractPromptGenerator):
    def generate_prompt(self):
        prompt_dict = {
            "systemRole": "You're a python developer. You need to create a python script file based on " + self.company_info + ". You need to create at least 300 lines of code.",
            "user": "Python developer working for a company as prompted from the system.",
            "context": self.company_info,
            "message": "Write a python script for this company to operate. It must be at least 300 lines of code.",
            "model" : "gpt-3.5-turbo",
        }
        return self.export_json(prompt_dict)

class PromptGenerator2(AbstractPromptGenerator):
    def generate_prompt(self):
        prompt_dict = {
            "systemRole": "You're a senior python developer. You need to optimize a python script file based on " + self.company_info + ". Ensure the script is highly efficient.",
            "user": "Senior Python developer working for a company as prompted from the system.",
            "context": self.company_info,
            "message": "Optimize a python script for this company to operate efficiently.",
            "model" : "gpt-3.5-turbo",
        }
        return self.export_json(prompt_dict)

class PromptGenerator3(AbstractPromptGenerator):
    def generate_prompt(self):
        prompt_dict = {
            "systemRole": "You're a python developer. You need to write test cases for a python script based on " + self.company_info + ". Ensure coverage for all major functions.",
            "user": "Python developer specializing in testing.",
            "context": self.company_info,
            "message": "Write test cases for a python script for this company. Ensure comprehensive coverage.",
            "model" : "gpt-3.5-turbo",
        }
        return self.export_json(prompt_dict)

