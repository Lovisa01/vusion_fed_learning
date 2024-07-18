import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(dotenv_path)

# Get the API key from the environment variable
API_KEY_COWRIE = os.getenv('MONGO_API_KEY_COWRIE')
#Base url for for prompts
COLLECTION_URL_COWRIE = os.getenv('COLLECTION_URL_COWRIE')

# Get the API key from the environment variable
API_KEY_PROMPT = os.getenv('MONGO_API_KEY_PROMPT')
#Base url for cowrie
COLLECTION_URL_PROMPT = os.getenv('COLLECTION_URL_PROMPT')

"""
Use getcowriepage to get the cowriepage contents.
"""

def getcowriepage(limit, skip):
    payload = json.dumps({
        "collection": "CowrieLogs",  # Replace with your collection name
        "database": "CowrieLogs",   # Replace with your database name
        "dataSource": "CowrieLogs",   # Replace with your data source name
        "filter": {},  # Empty filter to match all documents
        "limit": limit,
        "skip": skip
    })

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY_COWRIE,
    }
    url = COLLECTION_URL_COWRIE + "find"
    response = requests.post(url, headers=headers, data=payload)
    return response.json()


"""
Use getpromptpage to get the prompts contents.
"""

def getpromptpage(limit, skip):
    payload = json.dumps({
        "collection": "CowrieLogs",  # Replace with your collection name
        "database": "CowrieLogDB",   # Replace with your database name
        "dataSource": "CowrieLogs",   # Replace with your data source name
        "filter": {},  # Empty filter to match all documents
        "limit": limit,
        "skip": skip
    })

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY_PROMPT,
    }
    url = COLLECTION_URL_PROMPT + "find"
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

def getalldata(getpage):
    all_documents = []
    limit = 1000  # Set the limit to 1000
    skip = 0

    while True:
        documents = getpage(limit, skip)
        if not documents['documents']:
            break
        all_documents.extend(documents['documents'])
        skip += limit

    return all_documents


"""
Insert a prompt
"""
def insert_prompt(systemRole,user,context,message,outputContent):
    url = COLLECTION_URL_PROMPT + "insertOne"
    #Required format for inserting prompts
    payload = json.dumps({
        "collection": "CowrieLogs",
        "database": "CowrieLogs",
        "dataSource": "CowrieLogs",
        "document":  { 
            "role": systemRole,
            "user": user,
            "contentType": context,
            "prompt": message,
            "outputContent": outputContent,
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY_PROMPT,
    }
    #return to verify it provides an actual input
    response = requests.post(url, headers=headers, data=payload)
    print(response)
    return response

"""
Insert a log
"""

def insert_log(session_id, isAnalysed, src_ip, time_stamp, honeypot_name):
    url = COLLECTION_URL_COWRIE + "insertOne"
    #Required format for inserting prompts
    payload = json.dumps({
        "collection": "CowrieLogs",
        "database": "CowrieLogs",
        "dataSource": "CowrieLogs",
        "document":  { 
            "honeypot_name":honeypot_name,
            "session_id": session_id,
            "isAnalysed": isAnalysed,
            "src_ip": src_ip,
            "time_stamp": time_stamp,
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY_COWRIE,
    }
    #return to verify it provides an actual input
    response = requests.post(url, headers=headers, data=payload)
    print(response)
    return response

insert_log("test",True,"test", "test", "test")

