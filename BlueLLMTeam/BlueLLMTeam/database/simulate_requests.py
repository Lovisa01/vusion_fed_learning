from threading import Thread
from BlueLLMTeam.database.process_db import insert_documents_one, getpage, getalldata
from tqdm import tqdm
import json

# Define the absolute path to the script you want to run
script_name = r'C:\Users\Franklin Parker\Documents\AI Sweden\Code Base\vusion_fed_learning_Frank\BlueLLMTeam\BlueLLMTeam\database\log_db.py'

# Number of times to run the script
num_runs = 100000

data = (getalldata())
print(data)

# Using ThreadPoolExecutor to run the script multiple times in parallel
"""threads = []
for _ in range(num_runs):
    threads.append(Thread(target=insert_documents_one, kwargs={'documents': 'test'}))

for t in threads:
    t.start()

for t in tqdm(threads):
    t.join()

print("Finished running simulations.")"""
