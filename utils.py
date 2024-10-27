import os
from dotenv import load_dotenv
load_dotenv()


def load_access_token():    
    token_path = os.getenv('TOKEN_PATH')
    try:
        with open(token_path, 'r', encoding='utf-8') as file:
            access_token = file.read().strip()
        print("Access token loaded successfully.")
        print(f"Access token: {access_token[:10]}...{access_token[-10:]}")
        return access_token
    except FileNotFoundError:
        print(f"Error: The file {token_path} was not found.")
    except IOError:
        print(f"Error: Unable to read the file {token_path}.")
    
    print("Failed to load the access token.")
    return None
