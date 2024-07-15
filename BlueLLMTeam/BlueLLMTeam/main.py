import json
import logging

from tqdm import tqdm
from argparse import ArgumentParser
from dataclasses import dataclass

from BlueLLMTeam.agents import TeamLeaderRole, CowrieDesignerRole
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam.banner import TEAM_BANNER, LLM_DESIGNER, LLM_TEAM_LEAD
from BlueLLMTeam.monitor import monitor_logs
from BlueLLMTeam.utils.docker import verify_docker_installation


designers: list[CowrieDesignerRole] = []


@dataclass
class Arguments:
    context_file: str
    verbosity: int
    frequency: float
    yes: bool
    light_weight: bool
    max_honeypots: int
    logfile: str

    @classmethod
    def from_cli(cls):
        """
        Parse command line arguments
        """
        parser = ArgumentParser("blueLLMTeam", description="Activate the Blue Team of LLM agents")
        parser.add_argument("--context", "-c", help="JSON data with the job description")
        parser.add_argument("--verbose", "-v", action="count", default=0, help="Increase verbosity level")
        parser.add_argument("--frequency", "-f", type=float, default=1, help="Update frequency of the analyst")
        parser.add_argument("--yes", "-y", action="store_true", help="Skip all confirmations and allow all actions")
        parser.add_argument("--light-weight", "-l", action="store_true", help="Create a light weight file system without any file contents")
        parser.add_argument("--max-honeypots", "-m", type=int, default=-1, help="Do not deploy more honeypots than this")
        parser.add_argument("--logfile", "-L", type=str, default=None, help="Log file to write to")
        
        args = parser.parse_args()
        return cls(
            context_file=args.context,
            verbosity=args.verbose,
            frequency=args.frequency,
            yes=args.yes,
            light_weight=args.light_weight,
            max_honeypots=args.max_honeypots,
            logfile=args.logfile,
        )
    
    @property
    def verbose(self):
        return self.verbosity > 0
    
    def __str__(self):
        s = f"Context file: {self.context_file}"
        s += f"\nUpdate frequency: {self.frequency}"
        s += f"\nVerbosity level: {self.verbosity}"
        return s


def quit():
    # Cleanup designers
    for designer in designers:
        designer.stop()


def happy_with_llm_decision(prompt: str, yes: bool = False) -> bool:
    if yes:
        return True
    
    # Prompt until yes or no answer
    while True:
        a = input(f"{prompt} (y/n/r): ").lower()
        if a in ["y", "n", "r"]:
            break
        print(f"{a} is not a valid input. Only (y)es, (n)o, or (r)etry are valid")
    
    if a == "y":
        return True
    if a == "r":
        return False
    # Quit the application
    exit()

def config_logging(logfile: str, verbosity: int):
    log_level = logging.WARNING
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity > 1:
        log_level = logging.DEBUG
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    handlers = [stream_handler]
    if logfile is not None:
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(min(log_level, logging.INFO))
        handlers.append(file_handler)
    
    logging.basicConfig(level=min(log_level, logging.INFO), handlers=handlers)

def main():
    # Greeting
    print(TEAM_BANNER)
    print("\nChecking system...")

    # Parse CLI arguments
    args = Arguments.from_cli()

    # Configure logging
    config_logging(args.logfile, args.verbosity)

    # Verify docker
    if not verify_docker_installation():
        print("Failed to verify the docker installation...")
        return

    if args.verbose:
        print("\nRunning with the following arguments:")
        print(args)
    
    # Default context
    context = {
        "Organization": "HoneypotLLM",
        "Industry": "Cybersecurity",
        "Employees": 5,
    }
    # Update the default context
    if args.context_file is not None:
        with open(args.context_file, "r") as f:
            context.update(json.load(f))

    if args.verbose:
        print("\nJob information:")
        print(context)
    
    # Create LLM endpoint and team leader
    llm_endpoint = ChatGPTEndpoint()
    team_lead = TeamLeaderRole(llm_endpoint)

    # Decide on honeypots
    print(LLM_TEAM_LEAD)
    while True:
        print("\nThinking about what honeypots to deploy...")
        honeypot_count = team_lead.honeypot_amount(context)
        
        print("Team Lead wants to deploy the following honeypots: ")
        for honeypot_type, count in honeypot_count.items():
            print(f"- {honeypot_type}: {count}")

        if happy_with_llm_decision("Generate descriptions for all honeypots", args.yes):
            break

    for honey_type, count in honeypot_count.items():
        if args.max_honeypots != -1 and count > args.max_honeypots:
            honeypot_count[honey_type] = args.max_honeypots
    
    # Create honeypot descriptions
    while True:
        honeypot_descriptions = team_lead.honeypot_design(context, honeypot_count)

        print("Team Lead wants to deploy the following honeypots: ")
        for honeypot_description in honeypot_descriptions:
            print("#" * 30)
            print(f"name: {honeypot_description['name']}")
            print(f"type: {honeypot_description['type']}")
            print(f"description: {honeypot_description['description']}")
        print("#" * 30)
        
        if happy_with_llm_decision("Create honeypots according to the descriptions", args.yes):
            break

    # Design the contents of all honeypots
    print(LLM_DESIGNER)
    while True:
        print("Creating custom contents for all requested honeypots...")
        for honeypot_description in tqdm(honeypot_descriptions):
            designer = CowrieDesignerRole(
                llm_endpoint,
                honeypot_description["description"],
                light_weight=args.light_weight,
            )
            designers.append(designer)
            designer.create_honeypot()
        
        if happy_with_llm_decision("Deploy honeypots according to the descriptions", args.yes):
            break
    
    print("Deploying honeypots...")
    for designer in tqdm(designers):
        designer.deploy_honeypot()
    
    # Monitor attacker
    monitor_logs(args.frequency, args.verbosity)

    print("Stopping execution")


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Cleanup of containers and temporary files...")
        quit()
