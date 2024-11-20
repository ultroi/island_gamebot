import json

def load_config(file_path):
    """
    Loads a JSON configuration file.

    Args:
        file_path (str): The path to the JSON configuration file.

    Returns:
        dict: The configuration data if the file is found and is a valid JSON.
        None: If the file is not found or is not a valid JSON.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
        return None
    
def load_items_config(file_path: str) -> dict:
    """
    Load items configuration from a JSON file.
    
    Args:
        file_path (str): The path to the JSON file.
    
    Returns:
        dict: The items configuration dictionary.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            items_config = json.load(file)
        return items_config
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
        return None