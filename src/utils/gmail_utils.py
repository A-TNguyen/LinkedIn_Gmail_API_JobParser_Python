import base64
import email
from email import policy
from email.message import EmailMessage
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError

def get_label_id(service, label_name: str) -> Optional[str]:
    """
    Retrieves the Gmail Label ID for a given human-readable label name.

    Args:
        service: The authenticated Gmail API service object.
        label_name: The name of the label to find (e.g., "LinkedIn/Applied").

    Returns:
        The ID of the label, or None if not found.
    """
    try:
        results = service.users().labels().list(userId='me').execute()
        all_labels = results.get('labels', [])
        for label in all_labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        return None
    except Exception as e:
        print(f"Error getting label ID for {label_name}: {e}")
        return None

def fetch_messages(service, label_name: str, date_query: str = "") -> List[Dict]:
    """
    Fetches all message IDs from Gmail for a specific label, handling pagination.

    Args:
        service: The authenticated Gmail API service object.
        label_name: The name of the Gmail label to fetch emails from.
        date_query: Optional Gmail search query for date filtering (e.g., "after:2024/01/01")

    Returns:
        A list of message dictionaries, each containing an 'id'.
    """
    messages = []
    try:
        label_id = get_label_id(service, label_name)
        if not label_id:
            print(f"Label '{label_name}' not found.")
            return messages

        # Build search query combining label and date filter
        search_params = {
            'userId': 'me',
            'labelIds': [label_id],
            'maxResults': 500
        }
        
        # Add date query if provided
        if date_query:
            search_params['q'] = date_query
            print(f"Searching {label_name} with date filter: {date_query}")

        response = service.users().messages().list(**search_params).execute()
        
        total_messages = response.get('resultSizeEstimate', 0)
        if date_query:
            print(f"Found approximately {total_messages} messages in {label_name} (filtered)")
        else:
            print(f"Found approximately {total_messages} messages in {label_name}")
        
        messages.extend(response.get('messages', []))
        
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            print(f"Fetching next page for {label_name}...")
            search_params['pageToken'] = page_token
            response = service.users().messages().list(**search_params).execute()
            messages.extend(response.get('messages', []))
            
    except Exception as e:
        print(f"❌ Error fetching messages for {label_name}: {e}")
    
    print(f"✅ Successfully retrieved {len(messages)} messages from {label_name}")
    return messages

def get_full_message(service, msg_id: str) -> Optional[EmailMessage]:
    """
    Retrieves a single, complete email message by its ID.
    
    The message is fetched in 'raw' format and decoded into a standard
    Python email.message.Message object for easy parsing.

    Args:
        service: The authenticated Gmail API service object.
        msg_id: The ID of the message to retrieve.

    Returns:
        An email.message.Message object, or None if an error occurs.
    """
    try:
        msg_full = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        raw = base64.urlsafe_b64decode(msg_full['raw'].encode('ASCII'))
        return email.message_from_bytes(raw, policy=policy.default)
    except HttpError as error:
        print(f"HTTP error fetching message ID {msg_id}: {error}")
        return None 