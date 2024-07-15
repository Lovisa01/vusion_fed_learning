import os
from abc import abstractmethod

from BlueLLMTeam.agents.base import AgentRoleBase
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase


DEFAULT_PORT = os.environ.get("DEFAULT_PORT", 2222)


class HoneypotDesignerRole(AgentRoleBase):

    used_ports = set()

    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__(role="Honeypot Designer", llm_endpoint=llm_endpoint)
        self.port = None
    
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
    def deploy_honeypot(self):
        """
        Deploy a already created honeypot
        """

    def next_open_port(cls, start_port: int = DEFAULT_PORT) -> int:
        """
        Return the next open port, starting from start_port
        """
        while start_port in cls.used_ports:
            start_port += 1
        cls.used_ports.add(start_port)
        return start_port

    def stop(self):
        if self.port is not None:
            self.used_ports.discard(self.port)
