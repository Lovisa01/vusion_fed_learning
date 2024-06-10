from abc import ABC, abstractmethod


class LLMEndpointBase(ABC):

    @abstractmethod
    def ask(self, prompt_dict: dict[str, str]) -> str:
        """
        Ask the LLM endpoint something

        Arguments:
            prompt_dict: A dictionary with the following keys
                systemRole: The system prompt for this user
                user: The current user
                context: The previous context
                message: The message to the LLM agent
        
        Returns:
            response: response from LLM agent
        """


class EchoEndpoint(LLMEndpointBase):
    """
    Endpoint that can be used for testing. It echos the message back to the sender
    """
    def ask(self, prompt_dict: dict[str, str]) -> str:
        return prompt_dict["message"]


class ChatGPTEndpoint(LLMEndpointBase):
    pass


class Llama2Endpoint(LLMEndpointBase):
    pass
