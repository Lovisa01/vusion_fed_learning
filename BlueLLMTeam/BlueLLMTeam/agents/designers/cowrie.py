import os
import time
import shutil
import docker
import logging
from random import randint

from BlueLLMTeam.agents.designers.base import HoneypotDesignerRole
from BlueLLMTeam.agents.base import ROOT_DIR
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam.Honeypot.createFiles import generate_file_system, generate_random_id, generate_file_contents
from BlueLLMTeam.Honeypot.createfs import pickledir


HONEYPOT_FS = ROOT_DIR / "Honeypot/tmpfs"

logger = logging.getLogger(__name__)

AVAILABLE_HONEYPOTS = {
    "cowrie": "An SSH honeypot"
}
HONEYPOT_RESOURCES = "\n".join(f"- {honeypot}: {description}" for honeypot, description in AVAILABLE_HONEYPOTS.items())
EXAMPLE_OUTPUT = "\n".join(f"- {honeypot}: {randint(0, 5)}" for honeypot in AVAILABLE_HONEYPOTS.keys())



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

    def create_honeypot(self, honeypot_description: str, depth: int = 3, light_weight: bool = False) -> str:
        files = generate_file_system(
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
            light_weight=light_weight,
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
        image_name = os.environ.get("COWRIE_IMAGE")
        if image_name is None:
            logger.warning("COWRIE_IMAGE environment variable not set. Using default cowrie image.")
            image_name = "cowrie/cowrie:latest"
        try:
            if not client.images.list(name=image_name):
                raise docker.errors.ImageNotFound(f"Image {image_name} not found.")
            
            logger.info(f"Creating Cowrie container from image {image_name}...")

            self.port = self.next_open_port()
            self.cowrie_container = client.containers.run(
                image=image_name,
                detach=True,
                ports={"2222/tcp": self.port},
                volumes={
                    self.fake_fs_data / "custom.pickle": {"bind": "/cowrie/cowrie-git/share/cowrie/fs.pickle", "mode": "rw"},
                    self.fake_fs: {"bind": "/cowrie/cowrie-git/honeyfs/", "mode": "rw"}
                },
                environment={
                    "HONEYPOT_NAME": "cowrie-prod"
                },
            )
            logger.info(f"Successfully created Cowrie container ID: {self.cowrie_container.id}")

        except docker.errors.APIError as e:
            logger.error(f"Failed to create Cowrie container. Error: {e}")
            raise
        except docker.errors.ImageNotFound as e:
            logger.error(f"Could not find Cowrie image. Error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred when deploying Cowrie container. Error: {e}")
            raise

        while self.cowrie_container.status != "running":
            time.sleep(1)
            self.cowrie_container.reload()

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
