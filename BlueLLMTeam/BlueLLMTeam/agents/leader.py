import json
import logging
from random import randint

from BlueLLMTeam.agents.base import AgentRoleBase
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam.utils.text import extract_json_from_text, extract_markdown_list, replace_tokens


logger = logging.getLogger(__name__)


AVAILABLE_HONEYPOTS = {
    "cowrie": "An SSH honeypot"
}
HONEYPOT_RESOURCES = "\n".join(f"- {honeypot}: {description}" for honeypot, description in AVAILABLE_HONEYPOTS.items())
EXAMPLE_OUTPUT = "\n".join(f"- {honeypot}: {randint(0, 5)}" for honeypot in AVAILABLE_HONEYPOTS.keys())


class TeamLeaderRole(AgentRoleBase):
    """
    A role that acts as a team leader
    """

    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__(role="TeamLeader", llm_endpoint=llm_endpoint)

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError
    
    def honeypot_amount(self, context: dict, retries: int = 5) -> dict[str, int]:
        """
        Get the number of honeypots to deploy of each type
        """
        prompt = """
# Task Description
You are to generate a list of honeypots with the number of honeypots to deploy of each type from a given list of available honeypots. This list should be influenced by the company information provided.

# Company Information
{CONTEXT}

# Available Honeypots
{RESOURCES}

# Output Format
Generate a list in the following format:
- Honeypot Type: [Number of honeypots to deploy]

## Example Output
{EXAMPLE_OUTPUT}

# Generate the List
Based on the company information provided and the available honeypots, generate a list of honeypots with the recommended number of each type to deploy.
"""
        tokens = {
            "CONTEXT": json.dumps(context, indent=4),
            "RESOURCES": HONEYPOT_RESOURCES,
            "EXAMPLE_OUTPUT": EXAMPLE_OUTPUT,
        }
        prompt_dict = {
            "systemRole": self.prompts.get("System"),
            "user": "",
            "context": "",
            "message": replace_tokens(prompt, tokens),
        }

        for _ in range(retries):
            response = self.llm.ask(prompt_dict)
            # Parse out markdown list of honeypots from the LLM response
            try:
                honeypot_list = extract_markdown_list(response)
            except:
                logger.warning(f"Could not parse list from LLM response")
                continue
            # Parse out the count of each honeypot
            honeypot_count = {}
            for honeypot_list_item in honeypot_list:
                try:
                    honeypot_type, count = honeypot_list_item.split(':')
                except ValueError:
                    logger.warning(f"Bad format for LLM response for item {honeypot_list_item}")
                    continue
                
                # Remove non alphabetic characters from honeypot type
                honeypot_type = ''.join(filter(str.isalnum, honeypot_type)).lower()
                if honeypot_type not in AVAILABLE_HONEYPOTS.keys():
                    logger.warning(f"Requested honeypot {honeypot_type} not in the available resources")
                    continue
                # Remove non numeric characters from honeypot count
                count = ''.join(filter(str.isnumeric, count))
                if not count.isdigit():
                    logger.warning(f"Requested count is not a valid digit")
                    continue
                count = int(count)
                honeypot_count[honeypot_type] = count
        return honeypot_count
    
    def honeypot_design(self, context: dict, honeypot_count: dict[str, int], retries: int = 5) -> list[dict]:
        """
        Get the honeypot design for all requested honeypots
        """
        prompt = """
You are to deploy one or more honeypots to defend a business with the following information:
# Company Information
{CONTEXT}

You have been tasked to deploy {COUNT} honeypots of the type {TYPE}, {DESCRIPTION}. 

Please give a detailed description of each honeypot, so that a honeypot designer can later generate realistic contents for the honeypot.
Give your response as a json object so that it can be easily parsed. Give only a JSON object. The JSON should have the following structure:

[
    {
        "name": "Honeypot name",
        "description": "short but detailed description of the honeypots contents"
    },
]

Generate a list with {COUNT} honeypots.
"""
        for honeypot_type, count in honeypot_count.items():
            tokens = {
                "CONTEXT": json.dumps(context, indent=4),
                "TYPE": honeypot_type,
                "COUNT": count,
                "DESCRIPTION": AVAILABLE_HONEYPOTS[honeypot_type]
            }
            prompt_dict = {
                "systemRole": self.prompts.get("System"),
                "user": "",
                "context": "",
                "message": replace_tokens(prompt, tokens),
            }
            honeypot_descriptions = []
            for _ in range(retries):
                response = self.llm.ask(prompt_dict)
                try:
                    json_data = extract_json_from_text(response)
                except ValueError:
                    logger.warning("Failed to parse JSON data from team leader response")
                    continue
                # Check the contents
                try:
                    for item in json_data:
                        if "name" not in item or "description" not in item:
                            logger.warning("Response had wrong JSON format")
                            continue
                        item["type"] = honeypot_type
                except:
                    logger.warning("Response had wrong JSON format")
                    continue
                honeypot_descriptions.extend(json_data)
                break
            else:
                # No break encountered, retries failed
                raise ValueError(f"Failed to parse team leader response after {retries} attempts")
        return honeypot_descriptions
