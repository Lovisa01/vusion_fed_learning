import json
import os
import time
from threading import Lock

LOG_PROMPT_FILE_PATH = 'prompt_log.json'
LOG_COW_FILE_PATH = 'prompt_log.json'

FILE_LOCK = Lock()

def log_data(data, log_file_path):
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as file:
            json.dump([], file)

    with FILE_LOCK:
        with open(log_file_path, 'r') as file:
            data = json.load(file)

        data.append({"data": data, "timestamp": time.time()})
        print(f"Logging data: {data}")  # Debugging statement

        with open(log_file_path, 'w') as file:
            json.dump(data, file, indent=4)
