import os
import requests
import logging
import threading
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

#please update the endpoint url for DATA_PROMPT_COLLECTION_URL in the .env file
#please ask mahesh if you didn't found it
data_prompt_endpoint = os.getenv('DATA_PROMPT_COLLECTION_URL', None)
if data_prompt_endpoint is None:
    logger.warning("No data prompt endpoint provided. Prompts will not be logged")


def send_json_task(data: dict):
    """
    Send the json data
    """
    try:
        # Send the JSON object to the endpoint
        response = requests.post(data_prompt_endpoint, json=data, timeout=10)
        response.raise_for_status()

    except Exception as e:
        logger.warning(f"Failed to send prompt to the database: {e}")


def send_json(data_dict, outputContent):
    if data_prompt_endpoint is None:
        # No data endpoint provided
        return

    json_data = {
        "role": data_dict["systemRole"],
        "user": data_dict["user"],
        "contentType": data_dict["context"],
        "prompt": data_dict["message"],
        "outputContent": outputContent,
    }

    # Send the data in a separate thread, so that this one can immediately return
    threading.Thread(send_json_task, kwargs={"data": json_data}).start()
