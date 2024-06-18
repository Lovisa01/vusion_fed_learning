import json


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
