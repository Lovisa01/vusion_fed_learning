import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

#please update the endpoint url for DATA_PROMPT_COLLECTION_URL in the .env file
#please ask mahesh if you didn't found it
data_prompt_endpoint = os.getenv('DATA_PROMPT_COLLECTION_URL')

def send_json(data_dict, outputContent):
    json_data = {
        "role": data_dict["systemRole"],
        "user": data_dict["user"],
        "contentType": data_dict["context"],
        "prompt": data_dict["message"],
        "outputContent": outputContent,
    }

    try:
        # Send the JSON object to the endpoint
        response = requests.post(data_prompt_endpoint, json=json_data)
        response.raise_for_status()

        print(f"Response Code: {response.status_code}")

    except requests.exceptions.HTTPError as errhttp:
        print(f"HTTP Error: {errhttp}")
    except requests.exceptions.ConnectionError as errcon:
        print(f"Error Connecting: {errcon}")
    except requests.exceptions.Timeout as errtimeout:
        print(f"Timeout Error: {errtimeout}")
    except requests.exceptions.RequestException as err:
        print(f"An Error Occurred: {err}")
    return None