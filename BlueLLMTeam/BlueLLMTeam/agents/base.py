import os
import json
import logging
from pathlib import Path
from abc import ABC, abstractmethod

from BlueLLMTeam.LLMEndpoint import LLMEndpointBase


ROOT_DIR = Path(__file__).parent.parent
DEFAULT_PROMPT_CONFIGURATION_FILE = ROOT_DIR.parent / "prompts.json"
PROMPT_CONFIGURATION_FILE = os.environ.get("PROMPT_CONFIGURATION", DEFAULT_PROMPT_CONFIGURATION_FILE)

logger = logging.getLogger(__name__)


class AgentRoleBase(ABC):
    """
    Base class for all Agents

    Defines common behavior for them
    """

    def __init__(self, role: str, llm_endpoint: LLMEndpointBase, prompts: dict[str, str] = None) -> None:
        super().__init__()
        self.role = role

        # Load prompts from default configuration if no prompts are given
        self.prompts = prompts or self.load_prompts()

        self.llm = llm_endpoint

    def load_prompts(self) -> dict[str, str]:
        """
        Load prompts from a configuration file
        """
        with open(PROMPT_CONFIGURATION_FILE, "r") as f:
            prompt_conf = json.load(f)
        
        return prompt_conf[self.role]

    @abstractmethod
    def chat(self, conversation_history: list[dict]) -> str:
        """
        Engage in a conversation with other agents

        Arguments:
            conversation_history: A list of previous interactions
        
        Returns:
            response: The agents response
        """

