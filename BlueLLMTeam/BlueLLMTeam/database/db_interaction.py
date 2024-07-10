import os
import requests
import logging
import json
import aiohttp
import asyncio
import pandas as pd
from pathlib import Path
from tqdm import trange, tqdm

from dotenv import load_dotenv


load_dotenv()
BACKEND_IP = os.environ.get("BACKEND_IP")
BACKEND_PORT = os.environ.get("BACKEND_PORT")

LOGS_ENDPOINT = f"http://{BACKEND_IP}:{BACKEND_PORT}/logs"
ANALYZE_ENDPOINT = f"http://{BACKEND_IP}:{BACKEND_PORT}/analyse/logs"
ANALYZE_DONE_ENDPOINT = f"http://{BACKEND_IP}:{BACKEND_PORT}/logs/analyse"

logger = logging.getLogger(__name__)

LOCAL_LOG_DB_CACHE = Path(__file__).parent / "cache" / "logs.csv"


def add_log(log_record: dict) -> bool:
    """
    Add a log record to the database
    """
    data = json.dumps(log_record)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(LOGS_ENDPOINT, data=data, headers=headers)
    return response.ok


def get_all_sessions() -> set[str]:
    """
    Get all sessions
    """
    response = requests.get(LOGS_ENDPOINT)
    if not response.status_code == 200:
        return []
    data = response.json()
    sessions = set([item["session_id"] for item in data.get('data', {}).get('Items', [])])
    return sessions


def get_updated_sessions() -> list[str]:
    """
    Get all sessions that have been updated
    """
    # Get logs
    response = requests.get(ANALYZE_ENDPOINT)

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
    url = f"{LOGS_ENDPOINT}/{session_id}"
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
    url = f"{ANALYZE_DONE_ENDPOINT}/{session_id}"
    response = requests.put(url)
    return response.ok


async def get_session_logs(http_session: aiohttp.ClientSession, session_id: str, pbar: tqdm) -> tuple[str, list]:
    url = f"{LOGS_ENDPOINT}/{session_id}"
    try:
        async with http_session.get(url) as response:
            data = await response.json()
            pbar.update()
            return session_id, data
    except Exception:
        return session_id, None
    

async def get_all_session_logs(sessions: set[str], pbar: tqdm):
    async with aiohttp.ClientSession() as session:
            tasks = [get_session_logs(session, session_id, pbar) for session_id in sessions]
            results = await asyncio.gather(*tasks)
        
    data = []
    for session_id, interactions in results:
        if interactions is None:
            print(f"Failed to retrieve logs from session {session_id}")
            continue
        data.extend(interactions)

    return pd.DataFrame(data)
    

def fetch_all_session_logs(honeypot_names: list[str] = None, save_local_cache: bool = False) -> pd.DataFrame:
    sessions = get_all_sessions()

    # Load local logs from cache
    if LOCAL_LOG_DB_CACHE.exists():
        local_cache = pd.read_csv(LOCAL_LOG_DB_CACHE)
        # Remove sessions already in the database
        sessions = sessions - set(local_cache["session_id"])
    else:
        local_cache = None

    with trange(len(sessions), desc="Getting all logs from the database") as pbar:
        new_logs = asyncio.run(get_all_session_logs(sessions, pbar))
    
    if local_cache is None:
        logs = new_logs
    else:
        logs = pd.concat([local_cache, new_logs], ignore_index=True)

    if save_local_cache:
        LOCAL_LOG_DB_CACHE.parent.mkdir(exist_ok=True)
        logs.to_csv(LOCAL_LOG_DB_CACHE, header=True, index=False)
    
    if honeypot_names is None:
        return logs
    return logs[logs["honeypot_name"].isin(honeypot_names)]
