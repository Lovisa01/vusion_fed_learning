import os
import json
import time
import shutil
import docker
import logging
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from random import randint

from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam.Honeypot.createFiles import generate_file_system, generate_random_id, generate_file_contents
from BlueLLMTeam.Honeypot.createfs import pickledir
from BlueLLMTeam.utils import extract_json_from_text, extract_markdown_list, replace_tokens
from BlueLLMTeam.db_interaction import add_log


ROOT_DIR = Path(__file__).parent
DEFAULT_PROMPT_CONFIGURATION_FILE = ROOT_DIR.parent / "prompts.json"
PROMPT_CONFIGURATION_FILE = os.environ.get("PROMPT_CONFIGURATION", DEFAULT_PROMPT_CONFIGURATION_FILE)
HONEYPOT_FS = ROOT_DIR / "Honeypot/tmpfs"

logger = logging.getLogger(__name__)

AVAILABLE_HONEYPOTS = {
    "cowrie": "An SSH honeypot"
}
HONEYPOT_RESOURCES = "\n".join(f"- {honeypot}: {description}" for honeypot, description in AVAILABLE_HONEYPOTS.items())
EXAMPLE_OUTPUT = "\n".join(f"- {honeypot}: {randint(0, 5)}" for honeypot in AVAILABLE_HONEYPOTS.keys())


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
                honeypot_list = extract_markdown_list(response.content)
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
                response = self.llm.ask(prompt_dict).content
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

    def next_open_port(cls, start_port: int = 2222) -> int:
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


class CowrieDesignerRole(HoneypotDesignerRole):
    
    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__(llm_endpoint)
        self.cowrie_container = None
        self.honeypotfs_id = generate_random_id(8)

        # File locations
        self.fake_fs_data = HONEYPOT_FS / self.honeypotfs_id
        self.fake_fs = self.fake_fs_data / "honeyfs"

        # Container logs
        self.old_logs = set()
        self.logs_updated = False

    def create_honeypot(self, honeypot_description: str, depth: int = 3) -> str:
        files = generate_file_system(
            local_fs=self.fake_fs,
            current_folder="/home",
            honey_context=honeypot_description,
            llm=self.llm,
            max_depth=depth,
        )
        generate_file_contents(
            local_fs=self.fake_fs,
            files=files,
            honey_context=honeypot_description,
            llm=self.llm,
        )

        logger.info(f"Created honeypot filesystem at {self.fake_fs}")
 
        pickledir(self.fake_fs, depth, self.fake_fs_data / "custom.pickle")

        try:
            # Check if the source folder exists
            if not os.path.exists(ROOT_DIR / "Honeypot/_honeyfs"):
                logger.error(f"Source folder does not exist.")
                raise FileNotFoundError(f"Source folder for filesystem does not exist at {ROOT_DIR / 'Honeypot/_honeyfs'}")

            shutil.copytree(ROOT_DIR / "Honeypot/_honeyfs/etc", self.fake_fs / "etc")
            shutil.copytree(ROOT_DIR / "Honeypot/_honeyfs/proc", self.fake_fs / "proc")
            logger.info("Folder successfully copied.")
        
        except Exception as e:
            logger.error(f"An error occurred when copying honeyfs: {str(e)}")
            raise

    def deploy_honeypot(self):
        # Check if the honeypot is already deployed
        if self.cowrie_container is not None:
            raise ValueError("Cowrie container already deployed")

        client = docker.from_env()
        image_name = "cowrie/cowrie:latest"
        try:
            logger.info("Pulling Cowrie image...")
            client.images.pull(image_name)
            logger.info("Successfully pulled Cowrie image.")

            logger.info("Creating Cowrie container...")

            self.port = self.next_open_port()
            self.cowrie_container = client.containers.run(
                image=image_name,
                detach=True,
                ports={"2222/tcp": self.port},
                volumes={
                    self.fake_fs_data / "custom.pickle": {"bind": "/cowrie/cowrie-git/share/cowrie/fs.pickle", "mode": "rw"},
                    self.fake_fs: {"bind": "/cowrie/cowrie-git/honeyfs/", "mode": "rw"}
                    },
            )
            logger.info(f"Successfully created Cowrie container ID: {self.cowrie_container.id}")

        except docker.errors.APIError as e:
            logger.error(f"Failed to create Cowrie container. Error: {e}")
            raise
        except docker.errors.ImageNotFound as e:
            logger.error(f"Failed to pull Cowrie image. Error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred when deploying Cowrie container. Error: {e}")
            raise

        while self.cowrie_container.status != "running":
            time.sleep(1)
            self.cowrie_container.reload()

    def update_logs(self) -> str:
        # Check that the container is deployed
        if self.cowrie_container is None:
            raise ValueError("Cowrie container has not been deployed")

        # Cowrie log location
        cowrie_log = f"/cowrie/cowrie-git/var/log/cowrie/cowrie.json"
        tmp_log = f"/tmp/{self.cowrie_container.id}-cowrie.json"

        # Copy file from container to local filesystem
        docker_cp = ["docker", "cp", f"{self.cowrie_container.id}:{cowrie_log}", tmp_log]
        res = subprocess.run(docker_cp, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # Raise error if command failed
        if res.returncode != 0:
            logger.warning("Failed to copy logs from the docker container")
            return

        # Read file contents into the logs array
        with open(tmp_log, "r") as f:
            # One json record for each line
            for record in f:
                log = json.loads(record)
                if log.get("eventid") == "cowrie.command.input":
                    # Create a hash of the log (a sorted string)
                    log_hash = json.dumps(log, sort_keys=True)
                    # Only send log to database if it has not already been sent
                    if log_hash not in self.old_logs:
                        self.old_logs.add(log_hash)
                        self.logs_updated = True
                        # Send to database
                        data = {
                            "src_ip": log["src_ip"],
                            "session_id": log["session"],
                            "time_stamp": log["timestamp"],
                            "input_cmd": log["input"],
                            "honeypot_name": "cowrie",
                            "response_cmd": "",
                        }
                    
                        if not add_log(data):
                            logger.warning("Failed to add data to the database")
        # Remove tmp file
        if os.path.exists(tmp_log):
            os.remove(tmp_log)

    def stop(self):
        super().stop()
        if self.container_running():
            self.cowrie_container.stop()
            self.cowrie_container.remove()
            self.cowrie_container = None
        if os.path.exists(self.fake_fs_data):
            shutil.rmtree(self.fake_fs_data, ignore_errors=True)

    def container_running(self) -> bool:
        return self.cowrie_container is not None

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError("Not yet implemented")
