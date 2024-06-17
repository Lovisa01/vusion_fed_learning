import json
import time

from argparse import ArgumentParser
from dataclasses import dataclass

from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam.PromptDict import PromptGenerator

# EXAMPLE USAGE
prompt_gen = PromptGenerator(file_path="/bakery/finances/fiscalreport")
general_prompt = prompt_gen.python_coder()
print(general_prompt)

# Parse the JSON string back into a dictionary
python_prompt = (general_prompt)

llm_endpoint = ChatGPTEndpoint()

# Pass the dictionary instead of the JSON string
response = llm_endpoint.ask(python_prompt)
print(response.content)
