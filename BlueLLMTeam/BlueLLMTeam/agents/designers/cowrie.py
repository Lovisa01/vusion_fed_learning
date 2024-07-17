import os
import json
import time
import shutil
import docker
import logging
from random import randint
from tqdm import trange, tqdm
import threading

from BlueLLMTeam.agents.designers.base import HoneypotDesignerRole
from BlueLLMTeam.agents.base import ROOT_DIR
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam.Honeypot.createFiles import generate_file_system, generate_random_id, generate_file_contents
from BlueLLMTeam.Honeypot.createfs import pickledir
from BlueLLMTeam.agents.designers.cmd import CowrieCommandDesigner
from BlueLLMTeam.agents.designers.fs import copy_local_filenames
import BlueLLMTeam.PromptDict as prompt
from BlueLLMTeam.utils.path import conf


HONEYPOT_FS = ROOT_DIR / "Honeypot/tmpfs"

logger = logging.getLogger(__name__)

AVAILABLE_HONEYPOTS = {
    "cowrie": "An SSH honeypot"
}
HONEYPOT_RESOURCES = "\n".join(f"- {honeypot}: {description}" for honeypot, description in AVAILABLE_HONEYPOTS.items())
EXAMPLE_OUTPUT = "\n".join(f"- {honeypot}: {randint(0, 5)}" for honeypot in AVAILABLE_HONEYPOTS.keys())

linux_top_level_directories = [
    "bin",
    "boot",
    "dev",
    "etc",
    # "home", # Do not include
    "lib",
    "lib64",
    "media",
    "mnt",
    "opt",
    "proc",
    # "root", # Do not include
    "run",
    "sbin",
    "srv",
    "sys",
    "tmp",
    "usr",
    "var"
]

linux_system_files = [
    "proc/net/arp",
    "proc/mounts",
    "proc/version",
    "proc/meminfo",
    "proc/modules",
    "proc/cpuinfo",
    "etc/group",
    "etc/shadow",
    "etc/host.conf",
    "etc/issue",
    "etc/resolv.conf",
    "etc/hostname",
    "etc/hosts",
    "etc/inittab",
    "etc/passwd",
    "etc/motd",
]




class CowrieDesignerRole(HoneypotDesignerRole):
    
    def __init__(
            self, 
            llm_endpoint: LLMEndpointBase,
            honeypot_description: str,
            depth: int = 3,
            light_weight: bool = False
        ) -> None:
        super().__init__(llm_endpoint)
        self.cowrie_container = None
        self.honeypotfs_id = generate_random_id(8)

        # File locations
        self.honeypot_data = HONEYPOT_FS / self.honeypotfs_id
        self.fake_fs = self.honeypot_data / "honeyfs"
        self.pickle_fs = self.honeypot_data / "picklefs"
        self.txtcmds = self.honeypot_data / "txtcmds"
        self.honey_etc = self.honeypot_data / "etc"

        # Honeypot settings
        self.honeypot_description = honeypot_description
        self.depth = depth
        self.light_weight = light_weight

        # Container logs
        self.old_logs = set()
        self.logs_updated = False

    def create_honeypot(self) -> str:
        self.configure_cowrie()
        self.create_fake_filesystem()
        self.prepare_fake_commands()
        self.add_system_information_files()
        self.add_user_credentials()
        self.configure_banners_and_prompts()
        self.pickle_fake_filesystem()

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
                    self.honeypot_data / "custom.pickle": {"bind": "/cowrie/cowrie-git/share/cowrie/fs.pickle", "mode": "rw"},
                    self.txtcmds: {"bind": "/cowrie/cowrie-git/share/cowrie/txtcmds", "mode": "rw"},
                    self.fake_fs: {"bind": "/cowrie/cowrie-git/honeyfs/", "mode": "rw"},
                    self.honey_etc: {"bind": "/cowrie/cowrie-git/etc/", "mode": "rw"},
                },
                environment={
                    "HONEYPOT_NAME": os.environ.get("HONEYPOT_NAME", "cowrie")
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
        if os.path.exists(self.honeypot_data):
            shutil.rmtree(self.honeypot_data, ignore_errors=True)

    def container_running(self) -> bool:
        return self.cowrie_container is not None

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError("Not yet implemented")
    
    def configure_cowrie(self):
        """
        Set some basic configurations for cowrie
        """
        options = {
            "hostname": "sys03",
            "ssh_version": "OpenSSH_8.1p1, OpenSSL 1.1.1a  21 Aug 2021",
            "kernel_version": "3.8.1-4-amd64",
            "kernel_build_string": "#1 SMP Debian 3.3.92-1+deb8u2",
            "hardware_platform": "x86_64",
            "operating_system": "GNU/Linux",
            "version_ssh": "SSH-2.0-OpenSSH_5.5p1 Debian-6",
        }
        json_response = self.llm.ask(
            prompt_dict=prompt.cowrie_configuration_creator({"keys": options})
        ).content

        # Update options with LLM response
        json_data = json.loads(json_response)
        options.update(json_data)

        # Update cowrie configuration
        cowrie_conf = conf("cowrie.cfg").read_text()
        for key, value in options.items():
            cowrie_conf = cowrie_conf.replace(f"{{{key.upper()}}}", value, 1)

        # Write cowrie configuration
        self.honey_etc.mkdir(parents=True, exist_ok=True)
        (self.honey_etc / "cowrie.cfg").write_text(cowrie_conf)

    def create_fake_filesystem(self):
        """
        Create a fake filesystem for the honeypot
        """
        # Generate filesystem
        logger.info("Starting file generation for /home folder")
        files = generate_file_system(
            current_folder="/home",
            honey_context=self.honeypot_description,
            llm=self.llm,
            max_depth=self.depth,
        )
        generate_file_contents(
            local_fs=self.fake_fs,
            files=files,
            honey_context=self.honeypot_description,
            llm=self.llm,
            light_weight=self.light_weight,
        )

        logger.info(f"Created honeypot filesystem at {self.fake_fs}")

    def prepare_fake_commands(self):
        """
        Add fake commands to the cowrie container
        """
        command_designer = CowrieCommandDesigner(self.llm)
        command_responses = command_designer.generate_command_responses(100)

        pickle_bin_path = self.pickle_fs / "bin"
        pickle_bin_path.mkdir(exist_ok=True, parents=True)

        txtcmds_bin_path = self.txtcmds / "bin"
        txtcmds_bin_path.mkdir(exist_ok=True, parents=True)

        for full_cmd, response in command_responses:
            cmd = full_cmd.split(" ")[0].strip()

            if not cmd:
                # Ignore empty commands
                continue

            # Add to pickle
            cmd_path = pickle_bin_path / cmd
            cmd_path.touch()

            # Add to txtcmds
            response_path = txtcmds_bin_path / cmd
            response_path.write_text(response.strip() + "\n")

    def _add_system_file(self, file: str, pbar: tqdm) -> None:
        """
        Add contents to a system file
        """
        tokens = {
            "file": file
        }
        file_contents = self.llm.ask(prompt.linux_important_files_creator(tokens)).content
        
        file_path = self.fake_fs / file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_contents)
        pbar.update()

    def add_system_information_files(self):
        """
        Add contents to files containing system information
        """
        # Create a separate thread for each generation
        threads: list[threading.Thread] = []

        with trange(len(linux_system_files), desc="Generating system files", leave=False) as pbar:
            for file in linux_system_files:
                kwargs = {
                    "file": file,
                    "pbar": pbar,
                }
                t = threading.Thread(target=self._add_system_file, kwargs=kwargs)
                threads.append(t)
                    
            # Spawn new threads
            for t in threads:
                t.start()
            # Wait for all threads to complete
            for t in threads:
                t.join()

    def configure_banners_and_prompts(self):
        """
        Configure the look of the honeypot
        """
        pass

    def add_user_credentials(self):
        """
        Add users and passwords
        """
        pass

    def pickle_fake_filesystem(self):
        """
        Pickle the fake filesystem to show files in cowrie
        """
        # Copy all files from the fake filesystem to the pickle filesystem
        for p in self.fake_fs.rglob("*"):
            if p.is_file():
                pickle_path = self.pickle_fs / p.relative_to(self.fake_fs)
                pickle_path.parent.mkdir(parents=True, exist_ok=True)
                pickle_path.touch()

        # Add more files. Take them from the current filesystem
        for folder in linux_top_level_directories:
            try:
                copy_local_filenames(f"/{folder}", self.pickle_fs / folder, max_depth=4)
            except ValueError:
                pass

        # Pickle
        pickledir(self.pickle_fs, self.depth, self.honeypot_data / "custom.pickle")
