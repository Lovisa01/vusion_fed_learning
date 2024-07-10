import logging
from tqdm import trange, tqdm
from abc import abstractmethod

import BlueLLMTeam.PromptDict as prompt
from BlueLLMTeam.LLMEndpoint import LLMEndpointBase
from BlueLLMTeam.agents.base import AgentRoleBase
from BlueLLMTeam.utils.threading import ThreadWithReturnValue
from BlueLLMTeam.utils.path import conf as get_configuration_file
from BlueLLMTeam.database.db_interaction import fetch_all_session_logs


logger = logging.getLogger(__file__)


class CommandDesigner(AgentRoleBase):

    def __init__(self, llm_endpoint: LLMEndpointBase) -> None:
        super().__init__(role="Command Designer", llm_endpoint=llm_endpoint)

        self.known_commands = self.load_known_commands()
        self.seen_commands: dict[str, int] = {}
    
    @abstractmethod
    def load_known_commands(self) -> set[str]:
        """Load a list of known commands"""
    
    @abstractmethod
    def load_seen_commands(self) -> dict[str, int]:
        """
        Load a dictionary with all seen commands
        The key is the command, and the value is the frequency of that command
        """
    
    def command_known(self, cmd: str) -> bool:
        """
        Check if the command is known
        """
        # TODO: Make more complex
        return cmd.lstrip().split(" ")[0] in self.known_commands
    
    def freq_unknown_commands(self) -> dict[str, int]:
        """
        Get the frequency of all unknown commands
        """
        self.seen_commands = self.load_seen_commands()
        unknown_commands = {}
        for cmd, freq in self.seen_commands.items():
            if not self.command_known(cmd):
                unknown_commands[cmd] = freq
        return unknown_commands
    
    def generate_command_responses(self, k: int = None) -> list[tuple[str, str]]:
        """
        Generate command responses for the top-K commands

        Args:
            k: number of commands to generate. None to generate for all unknown commands
        """
        freq_unknown = self.freq_unknown_commands()

        if k is None:
            k = len(freq_unknown)
        
        # Extract top k
        sorted_items = sorted(freq_unknown.items(), key=lambda item: item[1], reverse=True)
        top_k = [item[0] for item in sorted_items[:k]]

        # Create a separate thread for each generation
        threads: list[ThreadWithReturnValue] = []

        with trange(len(top_k), desc="Generating command responses", leave=False) as pbar:
            for cmd in top_k:
                kwargs = {
                    "cmd": cmd,
                    "pbar": pbar,
                }
                t = ThreadWithReturnValue(target=self.generate_command_response, kwargs=kwargs)
                threads.append(t)
                    
                    
            # Spawn new threads
            for t in threads:
                t.start()
            
            # Wait for all threads to complete
            command_responses = {}
            for t in threads:
                cmd, response = t.join()
                if response is not None:
                    command_responses[cmd] = response
                
        return command_responses
    
    def generate_command_response(self, cmd: str, pbar: tqdm = None) -> str:
        """Generate the expected response for a linux command"""
        try:
            tokens = {
                "command": cmd,
            }
            response = self.llm.ask(prompt.linux_command_response(tokens)).content
        except Exception as e:
            logger.warning(f"Failed to generate response for command {cmd}: {e}")
            response = None
        if pbar is not None:
            pbar.update()
        return cmd, response

    def chat(self, conversation_history: list[dict]) -> str:
        raise NotImplementedError
    

class CowrieCommandDesigner(CommandDesigner):

    def load_known_commands(self) -> set[str]:
        # Read the known commands from a configuration file
        return set(get_configuration_file("cowrie_commands.txt").read_text().split())
    
    def load_seen_commands(self) -> dict[str, int]:
        logs = fetch_all_session_logs(save_local_cache=True, split_commands=True)
        return logs["input_cmd"].value_counts().to_dict()


if __name__ == "__main__":
    from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
    cmd_designer = CowrieCommandDesigner(ChatGPTEndpoint())
    print(cmd_designer.generate_command_responses(k=5))
