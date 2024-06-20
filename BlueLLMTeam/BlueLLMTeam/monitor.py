import time
import json
import logging

from BlueLLMTeam.RoleAgent import CowrieAnalystRole, CowrieDesignerRole
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam.banner import LLM_ANALYST
from BlueLLMTeam.db_interaction import get_logs_from_session, update_session_status, get_updated_sessions


logger = logging.getLogger(__name__)


def analyze_session(session_id: str, analyst: CowrieAnalystRole) -> None:
    """
    Analyze the logs from a session
    """
    logs = get_logs_from_session(session_id)
    if not logs:
        return
    
    update_session_status(session_id)
    print("##### Analyzing the following logs #####")
    print(logs)
    print("########################################")
    print("\nThinking...")
    response = analyst.analyse_logs(json.dumps(logs)).content
    print("##### Analyst result #####")
    print(response)
    print("##########################")


def monitor_logs(frequency: float, verbosity: int = 0):
    """
    Monitor all sessions logs and analyze them with an LLM
    Present the user with a description of the current threats and activities of the attacker
    """
    print(LLM_ANALYST)
    llm_endpoint = ChatGPTEndpoint()
    analyst = CowrieAnalystRole(llm_endpoint)
    print("Ready to analyse attackers. Waiting for connections...")

    prev_time = time.time_ns()
    try:
        while True:
            # Sleep until next loop
            curr_time = time.time_ns()
            exec_time = (curr_time - prev_time) / 1e9
            sleep_time = 1 / frequency - exec_time
            prev_time = curr_time
            
            if sleep_time > 0:
                if verbosity > 3:
                    print(f"Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)

            # Get updated sessions
            sessions = get_updated_sessions()
            if not sessions:
                continue

            for session_id in sessions:
                analyze_session(session_id, analyst)
    except KeyboardInterrupt:
        pass


def update_logs(frequency: float, designers: list[CowrieDesignerRole], verbosity: int = 0):
    prev_time = time.time_ns()
    while True:
        # Sleep until next loop
        curr_time = time.time_ns()
        exec_time = (curr_time - prev_time) / 1e9
        sleep_time = 1 / frequency - exec_time
        prev_time = curr_time

        if sleep_time > 0:
            if verbosity > 3:
                print(f"Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)

        stopped = 0
        for designer in designers:
            if designer.container_running():
                designer.update_logs()
            else:
                stopped += 1
        if stopped == len(designers):
            break

if __name__ == "__main__":
    monitor_logs(frequency=10, verbosity=0)
