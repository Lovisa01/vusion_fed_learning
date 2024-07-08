from pathlib import Path
import pandas as pd
import aiohttp
import asyncio
import requests
from tqdm import trange, tqdm


API_URL = "http://16.16.153.211:3000/logs"
DATABASE_PATH = Path(__file__).parent / "data" / "logs.csv"


# Function to make a single async API request
async def get_session_logs(http_session: aiohttp.ClientSession, session_id: str, pbar: tqdm) -> dict:
    url = API_URL + "/" + session_id
    try:
        async with http_session.get(url) as response:
            status = response.status
            data = await response.json()
            pbar.update()
            return session_id, status, data
    except aiohttp.ClientError as e:
        return session_id, None, {"message": str(e)}
    

async def fetch_all_sessions(sessions: list[str], pbar: tqdm):
    async with aiohttp.ClientSession() as session:
        tasks = [get_session_logs(session, session_id, pbar) for session_id in sessions]
        results = await asyncio.gather(*tasks)
    return results


def main():
    # Get all sessions from the database
    print("Retrieving all sessions from the database...")
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    sessions = [item["session_id"] for item in data.get('data', {}).get('Items', [])]
    print(f"Retrieving logs from all {len(sessions)} sessions...")

    with trange(len(sessions)) as pbar:
        results = asyncio.run(fetch_all_sessions(sessions, pbar))
    
    print("Save the logs to a local database...")
    data = []
    for session_id, status, d in results:
        if status != 200:
            print(f"Failed to retrieve logs from session {session_id}")
            continue
        data.extend(d)

    df = pd.DataFrame(data)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATABASE_PATH, header=True, index=False)
    print("Done!")


if __name__ == "__main__":
    main()