import time
import json
import logging
import pandas as pd

from BlueLLMTeam.agents import CowrieAnalystRole
from BlueLLMTeam.LLMEndpoint import ChatGPTEndpoint
from BlueLLMTeam.banner import LLM_ANALYST
from BlueLLMTeam.database.db_interaction import get_updated_sessions


logger = logging.getLogger(__name__)


def analyze_session(df: pd.DataFrame, analyst: CowrieAnalystRole, analyst_on: bool = True) -> None:
    """
    Analyze the logs from a session
    """
    # Sort the commands in the DataFrame
    sorted_commands = list(df.sort_values(by="time_stamp")["command"])
    print("##### Analyzing the following logs #####")
    logs_to_analyze = "\n".join(sorted_commands)
    print(logs_to_analyze)
    print("########################################")
    print("\nThinking...")
    if analyst_on:
        response = analyst.analyse_logs(logs_to_analyze)
    else:
        response = "Analyst is turned off"
    print("##### Analyst result #####")
    print(response)
    print("##########################")


def monitor_logs(frequency: float, verbosity: int = 0, analyst_on: bool = True):
    """
    Monitor all sessions logs and analyze them with an LLM
    Present the user with a description of the current threats and activities of the attacker
    """
    print(LLM_ANALYST)
    llm_endpoint = ChatGPTEndpoint()
    analyst = CowrieAnalystRole(llm_endpoint)
    print("Ready to analyse attackers. Waiting for connections...")

    prev_time = time.time_ns()
    while True:
        try:
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
            df = get_updated_sessions()
            if df.empty:
                continue
            
            sessions = set(df["session_id"])
            for session_id in sessions:
                analyze_session(df[df["session_id"] == session_id], analyst, analyst_on=analyst_on)
        except KeyboardInterrupt:
            logger.info("User interrupted main thread. Terminating program...")
            break
        except Exception as e:
            logger.warning(f"Error when analyzing the logs: {e}")
            pass


if __name__ == "__main__":
    monitor_logs(frequency=10, verbosity=0)
