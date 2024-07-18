import paramiko
import time

# Set SSH connection details
hostname = "13.60.57.51"
port = 22
username = "root"
password = ""  # Blank password

# Commands to run on the SSH server
commands = [
    "echo a"
]

# Create an SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the SSH server
client.connect(hostname, port=port, username=username, password=password)

# Open a shell channel
channel = client.invoke_shell()

# Function to send a command to the shell
def send_command(command):
    channel.send(command + '\n')
    output = channel.recv(1024).decode('utf-8')
    print(output)

# Loop to send commands 100 times
for i in range(1, 1500):
    print(f"Running iteration {i}")
    
    for command in commands:
        send_command(command)

    print(f"Iteration {i} completed")

print("Script execution completed 100 times.")
channel.close()
client.close()
