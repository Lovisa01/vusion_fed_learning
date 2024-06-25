import os
import requests
import logging
import json

from dotenv import load_dotenv

load_dotenv()
BACKEND_IP = os.environ.get("BACKEND_IP")
BACKEND_PORT = os.environ.get("BACKEND_PORT")

LOGS_ENDPOINT = "/logs"
ANALYZE_ENDPOINT = "/analyse/logs"
ANALYZE_DONE_ENDPOINT = "/logs/analyse"

logger = logging.getLogger(__name__)


def add_log(log_record: dict) -> bool:
    """
    Add a log record to the database
    """
    url = f"http://{BACKEND_IP}:{BACKEND_PORT}{LOGS_ENDPOINT}"
    data = json.dumps(log_record)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=data, headers=headers)
    return response.ok


def get_updated_sessions() -> list[str]:
    """
    Get all sessions that have been updated
    """
    # Get logs
    url = f"http://{BACKEND_IP}:{BACKEND_PORT}{ANALYZE_ENDPOINT}"
    response = requests.get(url)

    # Do some error checking on the response
    if not response.ok:
        logger.warning(f"Failed to retrieve updated sessions. Got status code {response.status_code} with response {response.content}")
        return []
    response_data = response.json()
    if "success" not in response_data:
        logger.warning(f"Response missing success key when retrieving updated sessions")
        return []
    
    # Extract session ids
    sessions = []
    try:
        items = response_data["data"]["Items"]
        for item in items:
            sessions.append(item["session_id"])
    except KeyError as e:
        logger.warning(f"Missing key in response: {e}")
        return []
    
    return sessions


def get_logs_from_session(session_id: str) -> list[dict]:
    """
    Get the logs from a session
    """
    print(f"\n###### New interaction with session {session_id} ######")
    url = f"http://{BACKEND_IP}:{BACKEND_PORT}{LOGS_ENDPOINT}/{session_id}"
    response = requests.get(url)

    # Extract logs
    if not response.ok:
        logger.warning(f"Failed to get logs from session {session_id}. Got status code {response.status_code} with response {response.content}")
        return []
    return response.json()


def update_session_status(session_id: str) -> bool:
    """
    Tell the server we will be analyzing the logs
    """
    url = f"http://{BACKEND_IP}:{BACKEND_PORT}{ANALYZE_DONE_ENDPOINT}/{session_id}"
    response = requests.put(url)
    return response.ok
