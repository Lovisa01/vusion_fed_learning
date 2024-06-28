import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

#please update the endpoint url for DATA_PROMPT_COLLECTION_URL in the .env file
#please ask mahesh if you didn't found it
data_prompt_endpoint = os.getenv('DATA_PROMPT_COLLECTION_URL', None)
if data_prompt_endpoint is None:
    logger.warning("No data prompt endpoint provided. Prompts will not be logged")

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

    try:
        # Send the JSON object to the endpoint
        response = requests.post(data_prompt_endpoint, json=json_data, timeout=1)
        response.raise_for_status()

    except requests.exceptions.HTTPError as errhttp:
        logger.warning(f"HTTP Error: {errhttp}")
    except requests.exceptions.ConnectionError as errcon:
        logger.warning(f"Error Connecting: {errcon}")
    except requests.exceptions.Timeout as errtimeout:
        logger.warning(f"Timeout Error: {errtimeout}")
    except requests.exceptions.RequestException as err:
        logger.warning(f"An Error Occurred: {err}")
