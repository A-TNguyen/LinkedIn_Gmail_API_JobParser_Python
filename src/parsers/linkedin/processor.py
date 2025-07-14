from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm
from utils.email_utils import parse_internal_date, extract_body, extract_applied_info, get_plain_text_body, get_html_body
from utils.date_utils import get_date_range_query, get_date_range_description
from .email_parsers import parse_applied_info, parse_viewed_rejected_info
import os
import base64
import email
from email import policy
import re
from datetime import datetime
import sys
from googleapiclient.errors import HttpError
import csv
import dateutil.parser as date_parser

LABELS = ['LinkedIn/Applied', 'LinkedIn/Viewed', 'LinkedIn/Rejected']
BASE_OUTPUT_FILE = 'data/processed/job_application_status'
ARCHIVE_DIR = 'data/archive'  # Use data/archive directory for consistency
BASE_FAILURE_LOG_FILE = 'data/processed/failed_verifications'

def get_output_directory() -> str:
    """Always use the processed directory for new files."""
    # Always use the processed directory for new files
    processed_dir = os.path.dirname(BASE_OUTPUT_FILE)
    os.makedirs(processed_dir, exist_ok=True)
    return processed_dir

def get_output_filename(date_range: str) -> str:
    """Generate output filename based on date range."""
    if date_range == "all":
        suffix = "all_time"
    elif date_range == "24h" or date_range == "1d":
        suffix = "last_24h"
    elif date_range == "7d" or date_range == "1w":
        suffix = "last_week"
    elif date_range == "30d" or date_range == "1m":
        suffix = "last_month"
    elif date_range == "90d" or date_range == "3m":
        suffix = "last_3months"
    elif date_range == "1y":
        suffix = "last_year"
    elif ":" in date_range:
        # Custom date range: 2024-01-01:2024-12-31
        start_date, end_date = date_range.split(":")
        suffix = f"custom_{start_date}_to_{end_date}"
    else:
        suffix = f"range_{date_range}"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = get_output_directory()
    return os.path.join(output_dir, f"job_application_status_{suffix}_{timestamp}.csv")

def get_failure_log_filename() -> str:
    """Generate single failure log filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{BASE_FAILURE_LOG_FILE}_{timestamp}.csv"

# Create necessary directories
os.makedirs('data/logs', exist_ok=True)
os.makedirs(os.path.dirname(BASE_OUTPUT_FILE), exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(BASE_FAILURE_LOG_FILE), exist_ok=True)

def get_status_priority(status: str) -> int:
    """Helper to determine priority for status updates."""
    return {"Rejected": 3, "Viewed": 2, "Applied": 1}.get(status, 0)

def get_label_id(service, label_name: str) -> Optional[str]:
    """Get the Gmail label ID for a given label name."""
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
    """Fetch messages from Gmail for a specific label with pagination and optional date filtering."""
    messages = []
    try:
        label_id = get_label_id(service, label_name)
        if not label_id:
            print(f"Label '{label_name}' not found.")
            return messages

        # Build search parameters
        search_params = {
            'userId': 'me',
            'labelIds': [label_id],
            'maxResults': 500
        }
        
        # Add date query if provided
        if date_query:
            search_params['q'] = date_query
            print(f"Searching {label_name} with date filter: {date_query}")

        # Initial request
        response = service.users().messages().list(**search_params).execute()
        
        # Get total count for progress tracking
        total_messages = response.get('resultSizeEstimate', 0)
        if date_query:
            print(f"Found approximately {total_messages} messages in {label_name} (filtered)")
        else:
            print(f"Found approximately {total_messages} messages in {label_name}")
        
        # Add first batch of messages
        messages.extend(response.get('messages', []))
        
        # Handle pagination
        page_count = 1
        while 'nextPageToken' in response:
            page_count += 1
            print(f"Fetching page {page_count} for {label_name}...")
            
            search_params['pageToken'] = response['nextPageToken']
            response = service.users().messages().list(**search_params).execute()
            messages.extend(response.get('messages', []))
            
            # Print progress
            print(f"Retrieved {len(messages)} messages so far...")
            
    except Exception as e:
        print(f"❌ Error fetching messages for {label_name}: {e}")
    
    print(f"✅ Successfully retrieved {len(messages)} messages from {label_name}")
    return messages

def write_data_to_csv(data: list, filename: str):
    """Writes a list of dictionaries to a CSV file."""
    # Ensure 'Location' is correctly placed after 'Date'
    fieldnames = ["Company Name", "Job Title", "Status", "Date", "Location", "Metadata Subject", "Comment"]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"❌ An error occurred while writing to '{filename}': {e}")

def write_failures_to_csv(failures, filename: str):
    file_exists = os.path.isfile(filename)
    fieldnames = ['Timestamp', 'Email ID', 'Label', 'Row Number', 'Total Emails', 'Reason', 'Date', 'Company Name', 'Job Title', 'Location', 'Status', 'Metadata', 'Comment', 'Source_File', 'Date_Range']
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(failures)
    except Exception as e:
        print(f"Error writing failures to CSV: {e}")

def process_gmail_labels_to_csv(service, target_labels_to_process: list, all_gmail_labels: list, date_range: str = "all"):
    """
    Fetches emails for specified labels, parses them, and consolidates into a single CSV file.
    Creates separate files for each date range with timestamps.
    """
    # --- Date Range Processing ---
    try:
        date_query = get_date_range_query(date_range)
        date_description = get_date_range_description(date_range)
        print(f"📅 Date range: {date_description}")
        if date_query:
            print(f"📅 Gmail search query: {date_query}")
    except ValueError as e:
        print(f"❌ Invalid date range: {e}")
        return False
    
    # Generate unique filenames for this date range
    output_file = get_output_filename(date_range)
    failure_log_file = get_failure_log_filename()
    
    print(f"📁 Output file: {output_file}")
    print(f"📁 Failure log: {failure_log_file}")

    job_applications = {}
    failure_log = []

    #<editor-fold desc="Phase 1: Build database from 'Applied' emails">
    print("\n--- Phase 1: Building database from 'LinkedIn/Applied' emails ---")
    if 'LinkedIn/Applied' in target_labels_to_process:
        messages = fetch_messages(service, 'LinkedIn/Applied', date_query)
        print(f"Found {len(messages)} 'Applied' emails to process.")
        for index, msg_info in enumerate(tqdm(messages, desc="Processing Applied"), 1):
            msg_full = get_full_message(service, msg_info['id'])
            if not msg_full: continue

            subject = msg_full['subject'] or "No Subject"
            date_str = parse_date_header(msg_full['date'])
            comment = generate_comment(subject)

            try:
                # Date Filter
                if date_str and int(date_str.split('-')[0]) < 2024: continue

                body = get_plain_text_body(msg_full)
                if not body:
                    raise ValueError("No plain text body found.")

                parsed_info = parse_applied_info(body)
                key = (parsed_info['Company Name'].lower().strip(), parsed_info['Job Title'].lower().strip())
                job_applications[key] = {
                    "Company Name": parsed_info['Company Name'],
                    "Job Title": parsed_info['Job Title'],
                    "Location": parsed_info['Location'],
                    "Status": "Applied",
                    "Date": date_str,
                    "Metadata Subject": subject,
                    "Comment": comment,
                }
            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp, 'Email ID': msg_info['id'], 'Label': 'LinkedIn/Applied',
                    'Row Number': index, 'Total Emails': len(messages), 'Reason': str(e), 
                    'Date': date_str, 'Company Name': 'N/A', 'Job Title': 'N/A',
                    'Location': 'N/A', 'Status': 'Applied', 'Metadata': subject, 'Comment': comment,
                    'Source_File': os.path.basename(output_file), 'Date_Range': get_date_range_description(date_range)
                })
                # --- LOG FAILURE BUT CONTINUE ---
                print(f"⚠️  WARNING: Failed to parse Applied email #{index}/{len(messages)} (ID: {msg_info['id']})")
                print(f"   Parser Error: {e}")
                print(f"   Continuing with remaining emails...")
                
                # Log the failure but don't stop processing
                write_failures_to_csv(failure_log, failure_log_file)
                continue
    print(f"✅ Successfully built database with {len(job_applications)} unique applications.")
    #</editor-fold>

    #<editor-fold desc="Phase 2: Process 'Viewed' and 'Rejected' emails">
    print("\n--- Phase 2: Processing 'Viewed' and 'Rejected' emails ---")
    labels_to_verify = [l for l in ['LinkedIn/Viewed', 'LinkedIn/Rejected'] if l in target_labels_to_process]

    for label_name in labels_to_verify:
        messages = fetch_messages(service, label_name, date_query)
        print(f"Found {len(messages)} '{label_name}' emails to process.")
        for msg_info in tqdm(messages, desc=f"Processing {label_name}"):
            msg_full = get_full_message(service, msg_info['id'])
            if not msg_full: continue

            subject = msg_full['subject'] or ""
            date_str = parse_date_header(msg_full['date'])
            comment = generate_comment(subject)
            current_status = label_name.split('/')[-1]
            parsed_info = {} # Ensure parsed_info exists

            try:
                # Date Filter
                if date_str and int(date_str.split('-')[0]) < 2024: continue

                html_body = get_html_body(msg_full)
                parsed_info = parse_viewed_rejected_info(html_body, subject)

                if parsed_info.get('error'):
                    raise ValueError(parsed_info['error'])

                company = parsed_info['Company Name']
                title = parsed_info['Job Title']
                location = parsed_info['Location']
                key = (company.lower().strip(), title.lower().strip())

                # Matching logic
                existing_record = job_applications.get(key)
                
                if not existing_record:
                    # If an application has no prior 'Applied' record, we'll create a new one.
                    # Try to get better location info by searching for Applied emails across all time
                    better_location = location
                    
                    # If location is missing or generic, try to find the original Applied email
                    if not location or location in ['Not Found', 'Location not specified', '']:
                        try:
                            # Search for Applied emails with same company/title across all time
                            applied_messages = fetch_messages(service, 'LinkedIn/Applied', "")
                            for applied_msg_info in applied_messages:
                                applied_msg_full = get_full_message(service, applied_msg_info['id'])
                                if not applied_msg_full:
                                    continue
                                
                                applied_body = get_plain_text_body(applied_msg_full)
                                if applied_body:
                                    try:
                                        applied_parsed = parse_applied_info(applied_body)
                                        applied_key = (applied_parsed['Company Name'].lower().strip(), 
                                                     applied_parsed['Job Title'].lower().strip())
                                        
                                        # If we found a matching Applied email, use its location
                                        if applied_key == key and applied_parsed.get('Location'):
                                            better_location = applied_parsed['Location']
                                            print(f"✅ Found matching Applied email location: {better_location}")
                                            break
                                    except:
                                        continue
                        except Exception as e:
                            print(f"⚠️ Could not search for Applied email location: {e}")
                    
                    # Log warning for unmatched records
                    if current_status == 'Viewed':
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        failure_reason = f"Unmatched 'Viewed' email. Added to main report, but a matching 'Applied' record was not found in the selected date range. Location: {better_location or 'Not Found'}"
                        failure_log.append({
                            'Timestamp': timestamp, 'Email ID': msg_info['id'], 'Label': label_name,
                            'Reason': failure_reason, 'Date': date_str, 
                            'Company Name': company, 'Job Title': title, 'Location': better_location or 'Not Found',
                            'Status': current_status, 'Metadata': subject, 'Comment': comment,
                            'Source_File': os.path.basename(output_file), 'Date_Range': get_date_range_description(date_range)
                        })
                    
                    # Add the new record for 'Viewed' or 'Rejected' with better location
                    job_applications[key] = {
                        "Company Name": company, 
                        "Job Title": title, 
                        "Location": better_location or "Location not found in date range", 
                        "Status": current_status,
                        "Date": date_str, 
                        "Metadata Subject": subject, 
                        "Comment": f"{current_status} email found without matching Applied record in date range"
                    }
                    continue

                # Update existing record - PRESERVE ORIGINAL LOCATION
                if get_status_priority(current_status) > get_status_priority(existing_record['Status']):
                    original_comment = existing_record.get('Comment', '')
                    original_location = existing_record.get('Location', '')  # Preserve original location
                    
                    # Only update status-related fields, preserve location from Applied email
                    existing_record['Status'] = current_status
                    existing_record['Date'] = date_str
                    existing_record['Metadata Subject'] = subject
                    existing_record['Comment'] = f"Status updated to {current_status}. Original comment: {original_comment}"
                    
                    # Keep the original location from Applied email, only fill if it was missing
                    if not original_location and location:
                        existing_record['Location'] = location
                    else:
                        existing_record['Location'] = original_location  # Preserve Applied email location

            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp, 'Email ID': msg_info['id'], 'Label': label_name,
                    'Reason': str(e), 'Date': date_str, 
                    'Company Name': parsed_info.get('Company Name', 'Parse Failed'),
                    'Job Title': parsed_info.get('Job Title', 'Parse Failed'), 
                    'Location': parsed_info.get('Location', 'Parse Failed'),
                    'Status': current_status, 'Metadata': subject, 'Comment': comment,
                    'Source_File': os.path.basename(output_file), 'Date_Range': get_date_range_description(date_range)
                })
    #</editor-fold>

    # --- Final Output ---
    if failure_log:
        write_failures_to_csv(failure_log, failure_log_file)
    
    final_data_list = list(job_applications.values())
    write_data_to_csv(final_data_list, output_file)
    
    print(f"\n\n==================== SCRIPT COMPLETE ====================")
    if not failure_log:
        print("✅ Run finished successfully with no errors.")
    else:
        print(f"⚠️  {len(failure_log)} non-critical errors were logged.")

    print("\n--- Files Written ---")
    absolute_output_path = os.path.abspath(output_file)
    print(f"📄 Main Report: {absolute_output_path}")

    if failure_log:
        absolute_failure_path = os.path.abspath(failure_log_file)
        print(f"📄 Error Log:   {absolute_failure_path}")
    print(f"==========================================================")
    
    return True

def get_full_message(service, msg_id):
    try:
        msg_full = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        raw = base64.urlsafe_b64decode(msg_full['raw'].encode('ASCII'))
        return email.message_from_bytes(raw, policy=policy.default)
    except HttpError as error:
        print(f"HTTP error fetching message ID {msg_id}: {error}")
        return None

def parse_date_header(date_string: str) -> str:
    """Parses date string from email header into YYYY-MM-DD format."""
    if not date_string:
        return ""
    try:
        # The dateutil parser is very robust and handles most common formats
        dt = date_parser.parse(date_string)
        return dt.strftime('%Y-%m-%d')
    except (date_parser.ParserError, TypeError):
        # Fallback for formats that parse might miss, e.g., with non-standard timezone names
        # Example: "Thu, 9 Nov 2023 15:53:11 +0000 (UTC)"
        match = re.search(r'\d+\s+\w+\s+\d{4}', date_string)
        if match:
            try:
                # Re-try parsing just the core date part
                dt = date_parser.parse(match.group(0))
                return dt.strftime('%Y-%m-%d')
            except (date_parser.ParserError, TypeError):
                return "" # Could not parse even the fallback
        return ""

def generate_comment(subject: str) -> str:
    """Generates a comment based on email subject line keywords."""
    if subject:
        return f"Email regarding: {subject}"
    return "No subject provided for comment."

def parse_messages(service, label_name: str) -> List[Dict]:
    """Parse messages for a specific label and extract relevant information."""
    # Use the full LinkedIn label name
    full_label = f"LinkedIn/{label_name}" if not label_name.startswith('LinkedIn/') else label_name
    print(f"\n📥 Parsing label: {label_name}")
    messages = fetch_messages(service, full_label, "")
    parsed_rows = []
    
    for msg_meta in tqdm(messages, desc=f"{label_name} Messages"):
        try:
            msg = service.users().messages().get(userId='me', id=msg_meta['id'], format='full').execute()
            payload = msg['payload']
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            subject = headers.get('Subject', '')
            date = parse_internal_date(msg['internalDate'])
            body = extract_body(payload)
            snippet = body[:300]

            if full_label == 'LinkedIn/Applied':
                company, title, location = extract_applied_info(body)
                if not company or not title or not location:
                    pd.DataFrame([{
                        'Subject': subject,
                        'Body': snippet,
                        'Date': date
                    }]).to_excel(f"data/logs/error_partial_{label_name}.xlsx", index=False)
                    raise ValueError(f"⚠️ Missing field in Applied: {subject}")
            else:
                company, title, location = '', '', ''

            parsed_rows.append({
                'Company Name': company,
                'Title': title,
                'Status': label_name,
                'Date': date,
                'Location': location,
                'Raw Subject': subject,
                'Email Body Snippet': snippet
            })

        except Exception as e:
            print(f"❌ Error parsing message: {e}")
            break

    return parsed_rows

def save_to_excel(applied_rows: List[Dict], viewed_rows: List[Dict], rejected_rows: List[Dict]):
    """Save parsed data to CSV file with separate files for each status."""
    # Save each status to its own CSV file
    pd.DataFrame(applied_rows).to_csv('data/processed/Applied.csv', index=False)
    pd.DataFrame(viewed_rows).to_csv('data/processed/Viewed.csv', index=False)
    pd.DataFrame(rejected_rows).to_csv('data/processed/Rejected.csv', index=False)
    print(f"\n✅ Exported to data/processed/")

def parse_html_for_job_info(html_content: str) -> dict:
    """
    Parses HTML content (from 'show original') to extract Job Title, Company Name, and Location.
    This is for 'Viewed' and 'Rejected' emails where the plain text is insufficient.
    """
    job_title = ""
    company_name = ""
    location = ""

    # Regex for Job Title - looks for text within <a> tag with specific styling/structure
    # This pattern is robust to HTML entities and non-breaking spaces.
    job_title_match = re.search(
        r'line-height:\s*1\.25;\s*color:\s*#0a66c2;">\s*(.*?)(?:</a>|</td)',
        html_content, re.DOTALL | re.IGNORECASE
    )
    if job_title_match:
        job_title = job_title_match.group(1).strip()
        job_title = job_title.replace('&amp;', '&').replace('&nbsp;', ' ').replace('=C2=A0', ' ')
        job_title = re.sub(r'\s+', ' ', job_title).strip() # Consolidate multiple spaces

    # Regex for Company Name and Location - looks for text within <p> tag with specific class, separated by &middot;
    company_location_match = re.search(
        r'<p\s+class=3D"text-system-gray-100\s+text-sm\s+leading-\[20px\]"[^>]*?>\s*(.*?)\s*&m=iddot;\s*(.*?)\s*</p>',
        html_content, re.DOTALL | re.IGNORECASE
    )
    
    if company_location_match:
        company_name = company_location_match.group(1).strip()
        location = company_location_match.group(2).strip()
        company_name = company_name.replace('&amp;', '&').replace('&nbsp;', ' ').replace('=C2=A0', ' ')
        location = location.replace('&amp;', '&').replace('&nbsp;', ' ').replace('=C2=A0', ' ')
        company_name = re.sub(r'\s+', ' ', company_name).strip()
        location = re.sub(r'\s+', ' ', location).strip()

    # Don't raise errors here, let the calling function decide how to handle missing data
    return {
        "Job Title": job_title,
        "Company Name": company_name,
        "Location": location
    } 