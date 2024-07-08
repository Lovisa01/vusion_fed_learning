import requests
import csv

def fetch_data_from_api(api_url):
    response = requests.get(api_url)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    json_response = response.json()
    return json_response

def write_to_csv(data, csv_filename):
    # Define CSV headers based on the structure of your data
    headers = ['Session_ID', 'src_ip', 'time_stamp', 'honeypotname', 'input_cmd']
    
    # Open the CSV file for writing
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        # Write each log entry to the CSV file
        for log in data:
            writer.writerow({
                'Session_ID': log['session_id'],
                'src_ip': log['src_ip'],
                'time_stamp': log['time_stamp'],
                'honeypotname': log.get('honeypotname') or log.get('honeypot_name', 'unknown'),  # Handle different key names
                'input_cmd': log['input_cmd']
            })

def main():
    api_url = 'http://16.16.153.211:3000/logs'  # Replace with your API URL
    response = fetch_data_from_api(api_url)
    items = response.get('data', {}).get('Items', [])
    
    all_logs = []
    for item in items:
        session_api_url = "http://16.16.153.211:3000/logs/" + item['session_id']
        logs = fetch_data_from_api(session_api_url)
        all_logs.extend(logs)
    
    # Write all logs to CSV
    csv_filename = 'logs_export.csv'
    write_to_csv(all_logs, csv_filename)
    print(f"Data exported to {csv_filename}")

if __name__ == '__main__':
    main()
