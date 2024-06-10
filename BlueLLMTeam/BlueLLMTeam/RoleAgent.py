import os
import json
from pathlib import Path
from abc import ABC, abstractmethod

from LLMEndpoint import LLMEndpointBase


DEFAULT_PROMPT_CONFIGURATION_FILE = Path(__file__).parent.parent / "prompts.json"
PROMPT_CONFIGURATION_FILE = os.environ.get("PROMPT_CONFIGURATION", DEFAULT_PROMPT_CONFIGURATION_FILE)


class AgentRoleBase(ABC):
    """
    Base class for all Agents

    Defines common behavior for them
    """

    def __init__(self, role: str, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__()
        self.role = role
        self.prompts = self.load_prompts()

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


class TeamLeaderRole(AgentRoleBase):
    """
    A role that acts as a team leader
    """

    def __init__(self) -> None:
        super().__init__("TeamLeader")


class AnalystRole(AgentRoleBase):
    """
    A role that acts as an analyst for attacker behavior
    """

    def __init__(self) -> None:
        super().__init__("Analyst")

    @abstractmethod
    def analyse_logs(self, container_id: str) -> str:
        """
        Analyse the logs from a container and return a reflection

        Arguments:
            container_id: id for the docker container to analyse the logs from

        Returns:
            response: Analyse of the logs
        """

    @abstractmethod
    def read_logs(self, container_id: str) -> str:
        """
        Read logs from a honeypot

        Arguments:
            container_id: id for the docker container to read the logs from
        """


class CowrieAnalystRole(AnalystRole):
    """
    An export on Cowrie analysis
    """

    def analyse_logs(self, container: str) -> str:
        logs = self.read_logs(container)
        prompt_dict = {
            "systemRole": self.prompts.get("System"),
            "user": self.role,
            "context": "",
            "message": logs,
        }
        return self.llm.ask(prompt_dict)

    def read_logs(self, container_id: str) -> str:
        return "pwd"


class HoneypotDesignerRole(AgentRoleBase):
    
    @abstractmethod
    def create_honeypot(self, honeypot_description: str) -> str:
        """
        Create a new honeypot

        Arguments:
            honeypot_description: A description for the honeypot and its data
        
        Returns:
            honeypot_id: A unique id for the honeypot
        """

    @abstractmethod
    def deploy_honeypot(self, honeypot_id: str):
        """
        Deploy a already created honeypot
        """


class CowrieDesignerRole(HoneypotDesignerRole):
    
    def create_honeypot(self, honeypot_description: str) -> str:
        # Create unique id
        # Create new folder for the data (named after the unique id)
        # Create honeyfs subfolder
        # Populate the fake filesystem with LLM and place data under honeyfs
        # Pickle fake filesystem into fs.pickle
        # Return unique id
