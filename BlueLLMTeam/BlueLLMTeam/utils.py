import json
import logging
import subprocess


def extract_json_from_text(text: str):
    """
    This function extracts JSON data enclosed in either square or curly brackets from a given string
    and loads it as a JSON object.

    :param text: String containing JSON data enclosed in square or curly brackets.
    :return: JSON object.
    :raises ValueError: If the extracted content is not valid JSON or no JSON data is found.
    """
    # Find the first opening bracket
    start = text.find('[')
    if start == -1:
        start = text.find('{')
    else:
        first_curly = text.find('{')
        if first_curly > -1:
            start = min(start, first_curly)
    if start == -1:
        raise ValueError("No opening bracket found")

    # Find the last closing bracket
    end = max(text.rfind(']'), text.rfind('}'))
    if end == -1 or end < start:
        raise ValueError("No matching closing bracket found")

    # Extract the JSON string
    json_str = text[start:end + 1]

    # Parse the JSON string to a Python object
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")

    return json_obj


def extract_markdown_list(markdown_text: str) -> list[str]:
    """
    Extracts a markdown list from a given string and returns it as a Python list.
    Only lines that start with '-' followed by a space are considered part of the list.
    
    Args:
        markdown_text (str): The input string containing the markdown list.
        
    Returns:
        list: A list of items from the markdown list.
    """
    # Split the input string into lines
    lines = markdown_text.split('\n')
    
    # Initialize an empty list to store the list items
    markdown_list = []
    
    # Iterate through each line in the input string
    for line in lines:
        # Strip leading and trailing whitespace from the line
        stripped_line = line.strip()
        
        # Check if the line starts with '-' or '*' followed by a space
        if stripped_line.startswith('- '):
            # Remove the leading '-' or '*' and space, and add the line to the markdown list
            markdown_list.append(stripped_line[2:].strip())
    
    return markdown_list


def replace_tokens(text: str, tokens: dict[str, str]):
    """
    Replace tokens in a text with new content
    """
    for token, replacement in tokens.items():
        text = text.replace(f"{{{token}}}", str(replacement))
    return text


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
    

