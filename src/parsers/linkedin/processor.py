import os
import json
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import modularized functions using absolute paths from 'src'
from utils.gmail_utils import fetch_messages, get_full_message
from utils.file_utils import write_data_to_csv, write_failures_to_csv, archive_report
from parsers.linkedin.email_parsers import (
    get_plain_text_body, get_html_body, parse_applied_info, 
    parse_viewed_rejected_info, parse_date_header, generate_comment
)

# Get the directory of the current file (processor.py) to build a robust path to its config.
_processor_dir = os.path.dirname(os.path.abspath(__file__))

# --- Configuration Loading ---
def load_parser_config():
    """Loads the LinkedIn-specific label configuration from its module directory."""
    config_path = os.path.join(_processor_dir, 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ CRITICAL: LinkedIn config file not found at {config_path}. Exiting.")
        return None
    except json.JSONDecodeError:
        print(f"❌ CRITICAL: Could not decode JSON from {config_path}. Check for syntax errors. Exiting.")
        return None

# --- Global Constants (loaded from .env) ---
OUTPUT_FILE = os.getenv('LINKEDIN_OUTPUT_FILE', 'data/processed/linkedin_job_status.csv')
ARCHIVE_DIR = os.getenv('LINKEDIN_ARCHIVE_DIR', 'data/processed/archive')
FAILURE_LOG_FILE = os.getenv('LINKEDIN_FAILURE_LOG', 'data/processed/failed_verifications.csv')

def get_status_priority(status: str, config: list) -> int:
    """Gets the priority for a status from the loaded configuration."""
    for item in config:
        if item['status'] == status:
            return item.get('priority', 0)
    return 0

def run(service):
    """The core function of the LinkedIn parser module."""
    
    # Load configuration
    label_config = load_parser_config()
    if not label_config:
        return False
        
    parser_map = {
        "applied": parse_applied_info,
        "viewed_rejected": parse_viewed_rejected_info
    }

    # Ensure all output directories exist.
    for path in [OUTPUT_FILE, ARCHIVE_DIR, FAILURE_LOG_FILE]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
    archived_file_path = archive_report(OUTPUT_FILE, ARCHIVE_DIR)
    job_applications = {}
    failure_log = []
    
    sorted_config = sorted(label_config, key=lambda x: (x.get('status') != 'Applied', x.get('priority', 0)))

    for config_item in sorted_config:
        label_name = config_item['label_name']
        status = config_item['status']
        parser_type = config_item['parser_type']
        parser_func = parser_map.get(parser_type)

        if not parser_func:
            print(f"⚠️ Warning: No parser found for type '{parser_type}' in config. Skipping '{label_name}'.")
            continue

        print(f"\n--- Processing Label: '{label_name}' (Status: {status}) ---")
        messages = fetch_messages(service, label_name)
        
        for msg_info in tqdm(messages, desc=f"Processing {status}"):
            msg_full = get_full_message(service, msg_info['id'])
            if not msg_full: continue

            subject = msg_full['subject'] or "No Subject"
            date_str = parse_date_header(msg_full['date'])
            comment = generate_comment(subject)
            parsed_info = {}
            
            try:
                if date_str and int(date_str.split('-')[0]) < 2024: continue

                if parser_type == 'applied':
                    body = get_plain_text_body(msg_full)
                    if not body: raise ValueError("No plain text body found.")
                    parsed_info = parser_func(body)
                    key = (parsed_info['Company Name'].lower().strip(), parsed_info['Job Title'].lower().strip())
                    job_applications[key] = {
                        "Company Name": parsed_info['Company Name'], "Job Title": parsed_info['Job Title'],
                        "Location": parsed_info['Location'], "Status": status, "Date": date_str,
                        "Metadata Subject": subject, "Comment": comment,
                    }
                else:
                    html_body = get_html_body(msg_full)
                    parsed_info = parser_func(html_body, subject)
                    if parsed_info.get('error'): raise ValueError(parsed_info['error'])

                    company = parsed_info['Company Name']
                    title = parsed_info['Job Title']
                    location = parsed_info['Location']
                    key = (company.lower().strip(), title.lower().strip())
                    
                    existing_record = job_applications.get(key)
                    
                    if not existing_record:
                        if status == 'Viewed':
                            reason = "Unmatched 'Viewed' email added to report. 'Applied' record not found."
                            failure_log.append({
                                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Email ID': msg_info['id'], 
                                'Label': label_name, 'Reason': reason, 'Date': date_str, 'Company Name': company, 
                                'Job Title': title, 'Location': location or 'Not Found', 'Status': status, 
                                'Metadata': subject, 'Comment': comment
                            })
                        job_applications[key] = {
                            "Company Name": company, "Job Title": title, "Location": location, "Status": status, 
                            "Date": date_str, "Metadata Subject": subject, "Comment": comment
                        }
                        continue

                    if get_status_priority(status, label_config) > get_status_priority(existing_record['Status'], label_config):
                        original_comment = existing_record.get('Comment', '')
                        existing_record.update({
                            "Status": status, "Date": date_str, "Metadata Subject": subject,
                            "Comment": f"Status updated to {status}. Original: {original_comment}"
                        })
                    
                    if not existing_record.get('Location') and location:
                        existing_record['Location'] = location

            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp, 'Email ID': msg_info['id'], 'Label': label_name, 'Reason': str(e),
                    'Date': date_str, 'Company Name': parsed_info.get('Company Name', 'Parse Failed'),
                    'Job Title': parsed_info.get('Job Title', 'Parse Failed'), 'Location': parsed_info.get('Location', 'Parse Failed'),
                    'Status': status, 'Metadata': subject, 'Comment': comment
                })
                if status == 'Applied':
                    print(f"\n\nCRITICAL ERROR: {e}. See log for details.")
                    write_failures_to_csv(failure_log, FAILURE_LOG_FILE)
                    return False
    
    if failure_log:
        write_failures_to_csv(failure_log, FAILURE_LOG_FILE)
    
    write_data_to_csv(list(job_applications.values()), OUTPUT_FILE)
    
    print(f"\n--- LinkedIn Parser Finished ---")
    print("\n--- Files Written by LinkedIn Parser ---")
    print(f"📄 Main Report: {os.path.abspath(OUTPUT_FILE)}")
    if archived_file_path:
        print(f"🗄️ Archive:     {archived_file_path}")
    if failure_log:
        print(f"📄 Error Log:   {os.path.abspath(FAILURE_LOG_FILE)}")
    
    return True 