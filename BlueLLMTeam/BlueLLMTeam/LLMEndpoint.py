#DECLARE ALL IMPORTS HERE.
#BEFORE RUNNING CHECK REQUIREMENTES ARE INSTALLED THANKS!
from abc import ABC, abstractmethod
from openai import OpenAI, RateLimitError
import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import ollama
import logging
import time
import random

from BlueLLMTeam.database import data_promts_endpoint
import threading
from random import choice
# YOU WILL HAVE TO LOAD FROM YOUR ENVINVORNMENT FILE
# Load environment variables from the .env file
load_dotenv()
# Get the OpenAI API key from the environment variables
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('GPT_KEY')
)

logger = logging.getLogger(__name__)

MAX_TIME_BETWEEN_RETRIES = float(os.getenv("MAX_TIME_BETWEEN_RETRIES", 2.0))
MAX_CHATGPT_REQUESTS = int(os.getenv("MAX_CHATGPT_REQUESTS", 16))
MAX_CHATGPT_TOKENS = int(os.getenv("MAX_CHATGPT_TOKENS", 2048))


class LLMEndpointBase(ABC):

    @abstractmethod
    def ask(self, prompt_dict: dict[str, str]) -> str:
        """
        Ask the LLM endpoint something

        Arguments:
            prompt_dict: A dictionary with the following keys:
                systemRole: The system prompt for the system to act as.
                user: The current user.
                context: The previous context.
                message: The message to the LLM agent.
                model: The designated model to be used.
                max_tokens: the largest amount of tokens allowed.

        
        Returns:
            response: response from LLM agent
        """
        pass

class EchoEndpoint(LLMEndpointBase):
    """
    Endpoint that can be used for testing. It echos the message back to the sender
    """
    def ask(self, prompt_dict: dict[str, str]):
        return prompt_dict["message"]


class ChatGPTEndpoint(LLMEndpointBase):

    def __init__(self, request_limit: int = MAX_CHATGPT_REQUESTS, token_limit: int = MAX_CHATGPT_TOKENS) -> None:
        super().__init__()
        self.request_limit = request_limit
        self.token_limit = token_limit
        self.locks = [threading.Lock() for _ in range(self.request_limit)]

    def get_random_lock(self):
        return choice(self.locks)

    def ask(self, prompt_dict: dict[str, str], max_retries: int = 3, retry: int = 0):
        try:
            # Create a prompt from the prompt_dict
            inputmessages = [
                {"role": "system", "content": prompt_dict['systemRole']},
                {"role": "user", "content": f"{prompt_dict['user']} {prompt_dict['context']} {prompt_dict['message']}"}
            ]

            if prompt_dict.get("json_format", False):
                response_format = { "type": "json_object" }
            else:
                response_format = {"type":"text"}

            # Make a request to the OpenAI API
            token_limit = min(self.token_limit, prompt_dict.get("max_tokens", self.token_limit))
            with self.get_random_lock():
                response = client.chat.completions.create(
                    model=prompt_dict.get("model", "gpt-3.5-turbo"),  # Specify the model you want to use
                    messages=inputmessages,
                    max_tokens=token_limit,
                    response_format=response_format,
                )
            data_promts_endpoint.send_json(data_dict=prompt_dict, outputContent=response.choices[0].message.content)
            return response.choices[0].message
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded. Will try {max_retries - retry} more times: {e.message}")
            if retry >= max_retries:
                raise
            time.sleep(random.random() * MAX_TIME_BETWEEN_RETRIES)
            return self.ask(prompt_dict=prompt_dict, max_retries=max_retries, retry=retry + 1)
        except Exception as e:
            logger.error(f"An error occurred when querying ChatGPT: {e}")
            raise


class Llama2Endpoint(LLMEndpointBase):

    def __init__(self, host: str = None) -> None:
        super().__init__()
        self.host = host
        self.client = ollama.Client(self.host)
    
    def ask(self, prompt_dict: dict[str, str]) -> str:
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
            logger.error(f"An error occurred: {e}")
            raise
