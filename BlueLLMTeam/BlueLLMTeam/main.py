import json
import time

from argparse import ArgumentParser
from dataclasses import dataclass

from BlueLLMTeam.RoleAgent import TeamLeaderRole, CowrieAnalystRole, CowrieDesignerRole
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint


@dataclass
class Arguments:
    context_file: str
    verbosity: int
    frequency: float

    @classmethod
    def from_cli(cls):
        """
        Parse command line arguments
        """
        parser = ArgumentParser("blueLLMTeam", description="Activate the Blue Team of LLM agents")
        parser.add_argument("--context", "-c", help="JSON data with the job description")
        parser.add_argument("--verbose", "-v", action="count", default=0, help="Increase verbosity level")
        parser.add_argument("--frequency", "-f", type=float, default=1, help="Update frequency of the analyst")
        
        args = parser.parse_args()
        return cls(
            context_file=args.context,
            verbosity=args.verbose,
            frequency=args.frequency,
        )
    
    @property
    def verbose(self):
        return self.verbosity > 0


def main():
    # Parse CLI arguments
    args = Arguments.from_cli()

    if args.verbose:
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
        print(context)
    
    # Create agents
    llm_endpoint = ChatGPTEndpoint()
    designer = CowrieDesignerRole(llm_endpoint)
    analyst = CowrieAnalystRole(llm_endpoint)

    # Design and deploy honeypot
    honeypot_id = designer.create_honeypot(json.dumps(context, indent=4))
    cowrie_container_id = designer.deploy_honeypot(honeypot_id)
    print("Waiting for container startup (20 seconds, temporarily hardcoded)")
    time.sleep(20)
    
    # Monitor attacker
    try:
        while True:
            start_time = time.time_ns()

            print(analyst.analyse_logs(cowrie_container_id).content)

            # Sleep until next loop
            exec_time = (time.time_ns() - start_time) / 1e9
            sleep_time = 1 / args.frequency - exec_time
            
            if sleep_time > 0:
                if args.verbosity > 3:
                    print(f"Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass

    print("Stopping execution")


if __name__ == "__main__":
    main()