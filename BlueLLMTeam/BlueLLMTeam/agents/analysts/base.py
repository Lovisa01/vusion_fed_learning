from abc import abstractmethod

from BlueLLMTeam.agents.base import AgentRoleBase
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase


class AnalystRole(AgentRoleBase):
    """
    A role that acts as an analyst for attacker behavior
    """

    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__(role="Analyst", llm_endpoint=llm_endpoint)

    @abstractmethod
    def analyse_logs(self, container_id: str) -> str:
        """
        Analyse the logs from a container and return a reflection

        Arguments:
            container_id: id for the docker container to analyse the logs from

        Returns:
            response: Analyse of the logs
        """