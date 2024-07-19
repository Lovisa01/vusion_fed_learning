import os
import requests
import logging
import json
import pandas as pd
from tqdm import trange, tqdm

from dotenv import load_dotenv

from threading import Thread
from BlueLLMTeam.utils.threading import ThreadWithReturnValue


load_dotenv()
API_KEY_COWRIE = os.getenv('MONGO_API_KEY_COWRIE')
COLLECTION_URL_COWRIE = os.getenv('COLLECTION_URL_COWRIE')
API_KEY_PROMPT = os.getenv('MONGO_API_KEY_PROMPT')
COLLECTION_URL_PROMPT = os.getenv('COLLECTION_URL_PROMPT')

PAGE_COUNT = 5000

logger = logging.getLogger(__name__)


def send_payload(payload: dict, destination: str, endpoint: str) -> requests.Response:
    """
    Build the payload
    """
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
    }
    if destination == "CowrieLogs":
        url = COLLECTION_URL_COWRIE + endpoint
        headers["api-key"] = API_KEY_COWRIE
    elif destination == "PromptLog":
        url = COLLECTION_URL_PROMPT + endpoint
        headers["api-key"] = API_KEY_PROMPT
    else:
        raise ValueError(f"Destination {destination} is not valid")
    
    _payload = {
        "collection": destination,
        "database": destination,
        "dataSource": destination,
    }
    _payload.update(payload)
    response = requests.post(url, headers=headers, data=json.dumps(_payload))

    # Log
    if not response.ok:
        logger.warning(f"Failed to send payload to {destination}: {response.text}")

    return response


def add_log(
        session_id: str,
        src_ip: str,
        time_stamp: str,
        honeypot_name: str,
        command: str,
) -> bool:
    """
    Add a log record to the database
    """
    document = {
        "document": {
            "session_id": session_id,
            "src_ip": src_ip,
            "time_stamp": time_stamp,
            "honeypot_name": honeypot_name,
            "command": command,
            "response": "",
            "isAnalyzed": False,
        }
    }
    response = send_payload(document, "CowrieLogs", "insertOne")
    return response.ok


def add_prompt(
        system_role: str,
        user: str,
        context: str,
        message: str,
        output: str,
        wait: bool = True,
) -> bool:
    """
    Add a prompt to the database
    """
    document = {
        "document":  { 
            "role": system_role,
            "user": user,
            "contentType": context,
            "prompt": message,
            "outputContent": output,
        }
    }
    kwargs = {
        "payload": document,
        "destination": "PromptLog",
        "endpoint": "insertOne",
    }
    if not wait:
        Thread(target=send_payload, kwargs=kwargs).start()
        return True
    response = send_payload(**kwargs)
    return response.ok


def get_item_count(destination: str) -> bool:
    """
    Get the total number of logs in the database
    """
    task = {
        "pipeline": [
            {"$count": "total"}
        ]
    }
    response = send_payload(task, destination, "aggregate")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('documents'):
            return data['documents'][0]['total']
        else:
            return 0
    else:
        logger.warning(f"Failed to get the record count: {response.status_code}, {response.text}")
        return None


def get_page(
        page: int,
        destination: str,
        content_filter: dict = {},
    ) -> list[dict]:
    """
    Get a page from the destination
    If a filter is provided the items will be filtered before being returned
    """
    payload = {
        "filter": content_filter,
        "limit": PAGE_COUNT,
        "skip": PAGE_COUNT * page,
    }
    response = send_payload(payload, destination, "find")
    documents = response.json()
    return documents.get("documents", [])


def get_all_items(destination: str, content_filter: dict = {}) -> pd.DataFrame:
    """
    Get all items from the database
    """
    count = get_item_count("CowrieLogs")
    if count is None:
        return []
    
    pages = count // PAGE_COUNT + 1
    
    def wrapper(page: int, pbar: tqdm) -> list[dict]:
        r = get_page(
            page=page,
            destination=destination,
            content_filter=content_filter,
        )
        pbar.update()
        return r

    threads: list[ThreadWithReturnValue] = []
    with trange(pages, desc="Retrieving all logs", leave=False) as pbar:
        for page in range(pages):
            kwargs = {
                "page": page,
                "pbar": pbar,
            }
            t = ThreadWithReturnValue(target=wrapper, kwargs=kwargs)
            threads.append(t)
    
        for t in threads:
            t.start()
        
        logs = []
        for t in threads:
            r = t.join()
            logs.extend(r)

    return pd.DataFrame(logs)


def update_items(destination: str, filter_criteria: dict, update_values: dict):
    """
    Update multiple items in the database
    """
    payload = {
        "filter": filter_criteria,
        "update": {"$set": update_values}
    }
    response = send_payload(payload, destination, "updateMany")
    if not response.ok:
        logger.warning(f"Did not update items correctly: {response.text}")


def get_updated_sessions() -> pd.DataFrame:
    """
    Get all sessions that have been updated
    """
    # Get logs
    is_analyzed_filter = {"isAnalyzed": False}
    new_logs = get_all_items("CowrieLogs", is_analyzed_filter)

    # Sort out all new sessions
    if "session_id" not in new_logs:
        return pd.DataFrame([])
    
    session_ids = list(set(new_logs["session_id"]))
    session_filter = {"session_id": {"$in": session_ids}}

    # Set all items in the sessions to Analyzed
    update_items("CowrieLogs", session_filter, {"isAnalyzed": True})

    # Return all logs in the sessions
    return get_all_items("CowrieLogs", session_filter)


def split_chained_commands(commands: pd.DataFrame) -> pd.DataFrame:
    """
    Split chained commands into parts
    """
    chain_symbols = ["&&", "||", ";", "|"]
    regex = "(?:" + "|".join(map(lambda s: s.replace("|", "\|"), chain_symbols)) + ")"
    expanded_commands = commands["input_cmd"].str.split(regex, regex=True)
    return commands.assign(input_cmd=expanded_commands).explode("input_cmd", ignore_index=True)


if __name__ == "__main__":
    # Add a new record
    # add_log(
    #     "simon-mongo-test2",
    #     "420.666.13.1",
    #     "2024-07-11T15:55:00Z",
    #     "simon-mongo-test",
    #     "mkdir simon-is-best",
    # )
    print(get_all_items("CowrieLogs").head(20))
    # print(get_updated_sessions())