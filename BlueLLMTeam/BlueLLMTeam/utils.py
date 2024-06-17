import json
import re

def extract_json_from_brackets(text):
    """
    This function extracts JSON data enclosed in either square or curly brackets from a given string
    and loads it as a JSON object.

    :param text: String containing JSON data enclosed in square or curly brackets.
    :return: JSON object.
    :raises ValueError: If the extracted content is not valid JSON or no JSON data is found.
    """
    # Use regular expression to find the content inside the square or curly brackets
    match = re.search(r'[\[{].*[\]}]', text)
    
    if not match:
        raise ValueError("No JSON data found inside square or curly brackets")
    
    # Extract the JSON string
    json_str = match.group(0)
    
    # Parse the JSON string to a Python object
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")
    
    return json_obj
