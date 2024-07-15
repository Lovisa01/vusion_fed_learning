import logging
import subprocess

def verify_docker_installation() -> bool:
    """
    Verify that docker has been installed and the daemon is running
    """
    # Check if docker is installed
    try:
        # Run the "docker --version" command and capture its output
        version_result = subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if the command was executed successfully
        if version_result.returncode == 0:
            # Print docker version and return True
            logging.info(f"Running tests with {version_result.stdout.strip()}")
        else:
            # Print the error and return False
            logging.critical(f"Error when testing docker installation: {version_result.stderr}")
            return False
    except FileNotFoundError:
        # This exception is raised if the "docker" command is not found, indicating Docker may not be installed
        logging.critical("Docker command not found. Is Docker installed?")
        return False
    
    # Check if the docker daemon is running
    try:
        # Ping the socket the daemon should be running on
        ping_result = subprocess.run(["curl", "-s", "--unix-socket", "/var/run/docker.sock", "http/_ping"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if ping_result.returncode == 0:
            return True
        else:
            logging.critical("Docker daemon is not running.")
            return False
    except FileNotFoundError:
        logging.critical("curl command not found. Is curl installed?")
        return False