from LLMEndpoint import ChatGPTEndpoint
from RoleAgent import CowrieDesignerRole

endpoint = ChatGPTEndpoint()

designer = CowrieDesignerRole(endpoint)

designer.deploy_honeypot(designer.create_honeypot("Cowrie Honeypot"))

