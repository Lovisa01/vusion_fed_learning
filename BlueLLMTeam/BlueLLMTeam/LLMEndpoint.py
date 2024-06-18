#DECLARE ALL IMPORTS HERE.
#BEFORE RUNNING CHECK REQUIREMENTES ARE INSTALLED THANKS!
from abc import ABC, abstractmethod
from openai import OpenAI
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Dict
import ollama

# YOU WILL HAVE TO LOAD FROM YOUR ENVINVORNMENT FILE
# Load environment variables from the .env file
load_dotenv()
# Get the OpenAI API key from the environment variables
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('GPT_KEY')
)

class LLMEndpointBase(ABC):

    @abstractmethod
    def ask(self, prompt_dict: Dict[str, str]) -> str:
        """
        Ask the LLM endpoint something

        Arguments:
            prompt_dict: A dictionary with the following keys:
                systemRole: The system prompt for this user
                user: The current user
                context: The previous context
                message: The message to the LLM agent
                model: The designated model to be used.
        
        Returns:
            response: response from LLM agent
        """
        pass

class EchoEndpoint(LLMEndpointBase):
    """
    Endpoint that can be used for testing. It echos the message back to the sender
    """
    def ask(self, prompt_dict: dict[str, str]) -> str:
        return prompt_dict["message"]


class ChatGPTEndpoint(LLMEndpointBase):

    def ask(self, prompt_dict: Dict[str, str]) -> str:
        try:
            # Create a prompt from the prompt_dict
            inputmessages = [
                {"role": "system", "content": prompt_dict['systemRole']},
                {"role": "user", "content": f"{prompt_dict['user']} {prompt_dict['context']} {prompt_dict['message']}"}
            ]

            # Make a request to the OpenAI API
            response = client.chat.completions.create(
                model=prompt_dict.get("model", "gpt-3.5-turbo"),  # Specify the model you want to use
                messages=inputmessages,
                max_tokens=2048
            )
            return response.choices[0].message
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


class Llama2Endpoint(LLMEndpointBase):

    def __init__(self, host: str = None) -> None:
        super().__init__()
        self.host = host
        self.client = ollama.Client(self.host)
    
    def ask(self, prompt_dict: Dict[str, str]) -> str:
        try:
            # Create a prompt from the prompt_dict
            inputmessages = [
                {"role": "system", "content": prompt_dict['systemRole']},
                {"role": "user", "content": f"{prompt_dict['user']} {prompt_dict['context']} {prompt_dict['message']}"}
            ]

            # Make a request to the OpenAI API
            response = self.client.chat(
                model=prompt_dict.get("model", "llama2-uncensored"),  # Specify the model you want to use
                messages=inputmessages
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
