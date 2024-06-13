import os
import json
import shutil
import docker
from pathlib import Path
from abc import ABC, abstractmethod

from LLMEndpoint import LLMEndpointBase
from Honeypot.createFiles import generate_files, generate_random_id
from Honeypot.createfs import pickledir

ROOT_DIR = Path(__file__).parent
DEFAULT_PROMPT_CONFIGURATION_FILE = ROOT_DIR.parent / "prompts.json"
PROMPT_CONFIGURATION_FILE = os.environ.get("PROMPT_CONFIGURATION", DEFAULT_PROMPT_CONFIGURATION_FILE)
HONEYPOT_FS = ROOT_DIR / "Honeypot/tmpfs"

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

    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__("Designer", llm_endpoint)
    
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
        honeypotfs_id = generate_random_id(8)

        #TODO: Move this prompt to Simon's prompt file
        # Prompt for the root directory of the file system
        root_dir_prompt = {
                "systemRole": "You're a linux terminal that needs to provide a file system for a car manufacturing company.",
                "user": "Linux developer",
                "context": "Filenames and file contents should be based on a car manufacturing company. The files should be files that you would find in an administrative file system of a car manufacturing company",
                "message": "Give an exmaple of the base directory of a linux file system, without explanatory text, folder names only, one folder per line, without any special characters or numbers, just the names of the folders",
                "model" : "gpt-3.5-turbo"
            }

        root_dir_response = self.llm.ask(root_dir_prompt)
        root_folders = root_dir_response.content.split("\n")

        generate_files(root_folders, HONEYPOT_FS / honeypotfs_id / "honeyfs", 0, 2, 2, 3, root_dir_prompt, self.llm)

        print("Created honeypot filesystem at", HONEYPOT_FS / honeypotfs_id)

        pickledir(HONEYPOT_FS / honeypotfs_id / "honeyfs", 3, HONEYPOT_FS / honeypotfs_id / "custom.pickle")

        try:
        # Check if the source folder exists
            if not os.path.exists(ROOT_DIR/"Honeypot/_honeyfs"):
                print(f"Source folder does not exist.")
                return

            shutil.copytree(ROOT_DIR/"Honeypot/_honeyfs/etc", HONEYPOT_FS / honeypotfs_id / "honeyfs/etc")
            shutil.copytree(ROOT_DIR/"Honeypot/_honeyfs/proc", HONEYPOT_FS / honeypotfs_id / "honeyfs/proc")
            print(f"Folder successfully copied.")
        
        except Exception as e:
            print(f"An error occurred when copying honeyfs: {str(e)}")

        return honeypotfs_id
        
    def deploy_honeypot(self, honeypot_id: str):
        client = docker.from_env()
        image_name = "cowrie/cowrie"
        try:
            print("Pulling Cowrie image...")
            image = client.images.pull(image_name)
            print("Successfully pulled Cowrie image.")

            print("Creating Cowrie container...")

            container = client.containers.run(
                image=image_name,
                detach=True,
                ports={"2222/tcp": 2222},
                volumes={
                    HONEYPOT_FS / honeypot_id / "custom.pickle": {"bind": "/cowrie/cowrie-git/share/cowrie/fs.pickle", "mode": "rw"},
                    HONEYPOT_FS / honeypot_id / "honeyfs": {"bind": "/cowrie/cowrie-git/honeyfs/", "mode": "rw"}
                    },
            )
            print("Successfully created Cowrie container ID: ", container.id)
            return container.id

        except docker.errors.APIError as e:
            print(f"Failed to create Cowrie container. Error: {e}")
        except docker.errors.ImageNotFound as e:
            print(f"Failed to pull Cowrie image. Error: {e}")
        except Exception as e:
            print(f"An error occurred when deploying Cowrie container. Error: {e}")

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError("Not yet implemented")
