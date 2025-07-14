import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables from a .env file for secure credential management.
load_dotenv()

# Define the scopes for the Gmail API.
# 'readonly' allows viewing messages, while 'modify' allows changing labels.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# --- Constants ---
# Scopes define the level of access you are requesting from the user.
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('TOKEN_PATH', 'token.json')

def get_credentials() -> Credentials:
    """
    Manages the OAuth 2.0 authentication flow for the Gmail API.

    This function handles loading, refreshing, and creating user credentials.
    - It first tries to load existing credentials from 'config/token.json'.
    - If the credentials have expired, it refreshes them using the refresh token.
    - If no valid credentials exist, it initiates a new OAuth 2.0 flow,
      prompting the user to authorize the application. The client ID and secret
      are loaded from environment variables.

    Returns:
        A valid Google OAuth2 Credentials object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                # If refresh fails, fall back to re-authentication
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file not found at {CREDENTIALS_PATH}. Please ensure it's in the root directory.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def save_credentials(creds: Credentials):
    """
    Saves the user's credentials to a file in JSON format.

    Args:
        creds: The Google OAuth2 Credentials object to save.
    """
    token_path = Path('config/token.json')
    token_path.parent.mkdir(exist_ok=True) # Ensure the 'config' directory exists.
    with open(token_path, 'w') as token:
        token.write(creds.to_json())

def authenticate():
    """
    The main authentication function called by the application.

    It retrieves valid credentials and uses them to build and return an
    authenticated Gmail API service object.

    Returns:
        A Google API service object for interacting with the Gmail API.
    
    Raises:
        Exception: If the authentication process fails for any reason.
    """
    try:
        creds = get_credentials()
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}") 