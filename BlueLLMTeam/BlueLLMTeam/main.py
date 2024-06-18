import json
import time

from argparse import ArgumentParser
from dataclasses import dataclass

from BlueLLMTeam.RoleAgent import TeamLeaderRole, CowrieAnalystRole, CowrieDesignerRole
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam.banner import TEAM_BANNER, LLM_DESIGNER, LLM_ANALYST, LLM_TEAM_LEAD


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
    
    def __str__(self):
        s = f"Context file: {self.context_file}"
        s += f"\nUpdate frequency: {self.frequency}"
        s += f"\nVerbosity level: {self.verbosity}"
        return s


def main():
    # Greeting
    print(TEAM_BANNER)

    # Parse CLI arguments
    args = Arguments.from_cli()

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

    # if not input("Deploy honeypots (y/n): ").lower() == "y":
    #     print("Stopping deployment...")
    #     return
    
    # Create agents
    llm_endpoint = ChatGPTEndpoint()
    team_lead = TeamLeaderRole(llm_endpoint)
    designer = CowrieDesignerRole(llm_endpoint)
    analyst = CowrieAnalystRole(llm_endpoint)

    # Decide on honeypots
    print(LLM_TEAM_LEAD)
    print("\nThinking about what honeypots to deploy...")
    honeypot_count = team_lead.honeypot_amount(context)

    print("Team Lead wants to deploy the following honeypots: ")
    for honeypot_type, count in honeypot_count.items():
        print(f"- {honeypot_type}: {count}")
    
    if not input("Generate honeypot descriptions (y/n): ").lower() == "y":
        print("Stopping deployment...")
        return
    
    honeypot_descriptions = team_lead.honeypot_design(context, honeypot_count)

    print("Team Lead wants to deploy the following honeypots: ")
    for honeypot_description in honeypot_descriptions:
        print("#" * 30)
        print(f"name: {honeypot_description['name']}")
        print(f"type: {honeypot_description['type']}")
        print(f"description: {honeypot_description['description']}")
        print("#" * 30)
    
    if not input("Deploy honeypots according to the descriptions (y/n): ").lower() == "y":
        print("Stopping deployment...")
        return

    # Design and deploy honeypot
    print(LLM_DESIGNER)
    print("Createing custom file system for honeypot...")
    designer.create_honeypot(json.dumps(context, indent=4))
    print("Deploying honeypot...")
    designer.deploy_honeypot()
    print("Waiting for container startup (20 seconds, temporarily hardcoded)")
    time.sleep(20)
    
    # Monitor attacker
    print(LLM_ANALYST)
    print("Ready to analyse attackers. Waiting for connections...")
    try:
        while True:
            start_time = time.time_ns()
            
            logs = designer.get_logs()
            if logs:
                print("\nNew interaction with the honeypot")
                print("##### Analyzing the following logs #####")
                print(logs)
                print("########################################")
                print("\nThinking...")
                response = analyst.analyse_logs(logs).content
                print("##### Analyst result #####")
                print(response)
                print("##########################")
                print("Waiting for more interactions...")

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
    print("Removing containers and temp files")
    designer.stop()


if __name__ == "__main__":
    main()
