from BlueLLMTeam.agents.analysts.base import AnalystRole


class CowrieAnalystRole(AnalystRole):
    """
    An export on Cowrie analysis
    """

    def analyse_logs(self, logs: str) -> str:
        prompt_dict = {
            "systemRole": self.prompts.get("System"),
            "user": "What is the hacker trying to do given these logs? Please provide your reasoning and end with a short conclusion.\n\n Here are the logs we have currently captured: \n\n",
            "context": "",
            "message": logs,
        }
        return self.llm.ask(prompt_dict)

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError
