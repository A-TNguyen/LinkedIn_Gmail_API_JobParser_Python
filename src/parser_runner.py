import base64
import email
from email import policy
from googleapiclient.errors import HttpError
from tqdm import tqdm
import re
import csv
import os
from datetime import datetime
from dateutil import parser as date_parser

def get_plain_text_body(msg) -> str:
    """Parses an email message and returns the plain text body."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition')):
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception:
                    return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception:
            return msg.get_payload(decode=True).decode('latin-1', errors='ignore')
    return ""

def get_html_body(msg) -> str:
    """Parses an email message and returns the HTML body."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html' and 'attachment' not in str(part.get('Content-Disposition')):
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception:
                    return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    else:
        ctype = msg.get_content_type()
        if ctype == 'text/html':
            try:
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception:
                return msg.get_payload(decode=True).decode('latin-1', errors='ignore')
    return ""

def parse_applied_info(plain_text_body: str) -> dict:
    job_title, company_name, location = "", "", ""
    lines = plain_text_body.splitlines()
    try:
        start_index = next(i for i, line in enumerate(lines) if "Your application was sent to" in line)
        relevant_lines = [line.strip() for line in lines[start_index + 1:] if line.strip()]
        if len(relevant_lines) >= 3:
            job_title, company_name, location = relevant_lines[0], relevant_lines[1], relevant_lines[2]
    except (StopIteration, IndexError):
        pass  # Will be caught by validation below

    if not all([job_title, company_name, location]):
        missing_fields = []
        if not job_title: missing_fields.append("Job Title")
        if not company_name: missing_fields.append("Company Name")
        if not location: missing_fields.append("Location")
        raise ValueError(f"Could not parse required fields. Missing: {', '.join(missing_fields)}")
        
    return {"Job Title": job_title, "Company Name": company_name, "Location": location}

def parse_viewed_rejected_info(html_content: str, subject: str) -> dict:
    job_title, company_name, location = "", "", ""
    error_message = None
    
    # Try parsing HTML first for rich data
    company_location_match = re.search(r'<p[^>]*?>\s*([^<]+?)\s*·\s*(.*?)\s*</p>', html_content, re.IGNORECASE)
    if company_location_match:
        company_name = company_location_match.group(1).strip()
        location = company_location_match.group(2).strip()
    
    job_title_match = re.search(r'color:\s*#0a66c2;">\s*([^<]+?)\s*<', html_content, re.IGNORECASE)
    if job_title_match:
        job_title = job_title_match.group(1).strip()
        
    # Fallback to subject line parsing, which is very reliable for some templates
    if 'viewed by' in subject.lower():
        match = re.search(r'Your application was viewed by\s+(.*)', subject, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
    
    if 'application to' in subject.lower() and 'at' in subject.lower():
         match = re.search(r'Your application to\s+(.*?)\s+at\s+(.*)', subject, re.IGNORECASE)
         if match:
             job_title = match.group(1).strip()
             company_name = match.group(2).strip()
    
    # Clean up results
    if company_name: company_name = company_name.replace('&amp;', '&').strip()
    if job_title: job_title = job_title.replace('&amp;', '&').strip()
    if location: location = location.replace('&amp;', '&').strip()

    # CRITICAL: If company_name is still not found, set an error message.
    if not company_name:
        error_message = "Critical parse failure: Could not determine Company Name from HTML or Subject."

    return {"Job Title": job_title, "Company Name": company_name, "Location": location, "error": error_message}

def parse_date_header(date_string: str) -> str:
    """Parses date string from email header into YYYY-MM-DD format."""
    if not date_string:
        return ""
    try:
        dt = date_parser.parse(date_string)
        return dt.strftime('%Y-%m-%d')
    except (date_parser.ParserError, TypeError):
        return ""

def generate_comment(subject: str) -> str:
    """Generates a comment based on the email subject."""
    if subject:
        return f"Email regarding: {subject}"
    return "No subject found."

def run_verification_test(service):
    """
    Verifies that 'Viewed' and 'Rejected' emails correspond to an 'Applied' email with a location.
    """
    print("--- Starting Verification Test ---")
    failure_log = []
    
    # Step 1: Build a database of all applied applications
    print("\n--- Phase 1: Building database from 'LinkedIn/Applied' emails ---")
    applied_jobs = {} # Key: (company, title), Value: location
    try:
        messages = fetch_all_messages_for_label(service, 'LinkedIn/Applied')
        print(f"Found {len(messages)} 'Applied' emails to process.")
        for msg_info in tqdm(messages, desc="Processing Applied"):
            msg_full = get_full_message(service, msg_info['id'])
            if not msg_full: continue

            body = get_plain_text_body(msg_full)
            subject = msg_full['subject'] or "No Subject"
            try:
                parsed_info = parse_applied_info(body)
                key = (parsed_info['Company Name'].lower(), parsed_info['Job Title'].lower())
                applied_jobs[key] = parsed_info['Location']
            except ValueError as e:
                date_str = parse_date_header(msg_full['date'])
                comment = generate_comment(subject)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp,
                    'Email ID': msg_info['id'], 
                    'Label': 'LinkedIn/Applied', 
                    'Reason': f"Critical parse failure: {e}", 
                    'Date': date_str,
                    'Company Name': 'N/A',
                    'Job Title': 'N/A',
                    'Location': 'N/A',
                    'Status': 'Applied',
                    'Metadata': subject,
                    'Comment': comment
                })
                print(f"\nCRITICAL: Could not parse 'Applied' email (ID: {msg_info['id']}, Subject: {subject}). Error: {e}")
                print("Stopping test. All 'Applied' emails must be parsable and contain a location.")
                write_failures_to_csv(failure_log)
                return False
        print(f"Successfully built database with {len(applied_jobs)} unique applications.")

    except Exception as e:
        print(f"\nFAIL: An error occurred during Phase 1: {e}")
        return False
        
    # Step 2: Verify 'Viewed' and 'Rejected' emails against the database
    print("\n--- Phase 2: Verifying 'Viewed' and 'Rejected' emails ---")
    found_matches = 0
    test_passed = True
    labels_to_verify = ['LinkedIn/Viewed', 'LinkedIn/Rejected']

    for label_name in labels_to_verify:
        print(f"\nVerifying label: {label_name}")
        messages = fetch_all_messages_for_label(service, label_name)
        print(f"Found {len(messages)} '{label_name}' emails to verify.")
        for msg_info in tqdm(messages, desc=f"Verifying {label_name}"):
            msg_full = get_full_message(service, msg_info['id'])
            if not msg_full: continue

            subject_header = msg_full['subject'] or ""
            html_body = get_html_body(msg_full)
            date_str = parse_date_header(msg_full['date'])
            comment = generate_comment(subject_header)
            current_status = label_name.split('/')[-1]

            parsed_info = parse_viewed_rejected_info(html_body, subject_header)
            
            # Check if the parser returned an error
            if parsed_info['error']:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp,
                    'Email ID': msg_info['id'], 
                    'Label': label_name, 
                    'Reason': parsed_info['error'],
                    'Date': date_str,
                    'Company Name': parsed_info['Company Name'] or 'Not Found',
                    'Job Title': parsed_info['Job Title'] or 'Not Found',
                    'Location': parsed_info['Location'] or 'Not Found',
                    'Status': current_status,
                    'Metadata': subject_header,
                    'Comment': comment
                })
                print(f"\n\n==================== TEST FAILED ====================")
                print(f"❌ FAIL: Could not correctly parse '{label_name}' email (ID: {msg_info['id']}).")
                print(f"   Reason: {parsed_info['error']}")
                print(f"=========================================================")
                test_passed = False
                break # Stop processing this label

            company, title = parsed_info['Company Name'], parsed_info['Job Title']
            key = (company.lower(), title.lower())
            
            if key in applied_jobs:
                location = applied_jobs[key]
                if not location:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    failure_log.append({
                        'Timestamp': timestamp,
                        'Email ID': msg_info['id'], 
                        'Label': label_name, 
                        'Reason': 'Matched "Applied" record is MISSING a location.',
                        'Date': date_str,
                        'Company Name': company,
                        'Job Title': title,
                        'Location': 'MISSING IN SOURCE',
                        'Status': current_status,
                        'Metadata': subject_header,
                        'Comment': comment
                    })
                    print(f"\n\n==================== TEST FAILED ====================")
                    print(f"❌ FAIL: Match found for '{company} - {title}', but the original 'Applied' record is MISSING a location.")
                    print(f"=========================================================")
                    test_passed = False
                    break
                
                print(f"\nSUCCESS: Found match for '{label_name}' email. Location: {location}")
                found_matches += 1
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                failure_log.append({
                    'Timestamp': timestamp,
                    'Email ID': msg_info['id'], 
                    'Label': label_name, 
                    'Reason': f"No matching 'Applied' record found for Company '{company}' and Title '{title}'.",
                    'Date': date_str,
                    'Company Name': company,
                    'Job Title': title,
                    'Location': parsed_info.get('Location', 'N/A'),
                    'Status': current_status,
                    'Metadata': subject_header,
                    'Comment': comment
                })
                print(f"\nINFO: No matching 'Applied' record found for {label_name} email: '{company} - {title}'")
        
        if not test_passed:
            break

    print("\n--- Verification Test Complete ---")
    if failure_log:
        print(f"\nFound {len(failure_log)} verification failures.")
        write_failures_to_csv(failure_log)
    
    if not test_passed:
        return False
        
    # Test now passes only if there are NO failures.
    if not failure_log and found_matches > 0:
        print(f"✅ Success: Verified {found_matches} 'Viewed'/'Rejected' emails. No failures found.")
        return True
    elif not failure_log and found_matches == 0:
        print("✅ Success: No 'Viewed' or 'Rejected' emails needed verification. No failures found.")
        return True
    else:
        print(f"❌ Fail: {len(failure_log)} verification failures were found. See failed_verifications.csv for details.")
        return False
        

def write_failures_to_csv(failures):
    """Writes failure log to a CSV file, appending to it if it already exists."""
    output_file = 'data/processed/failed_verifications.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    file_exists = os.path.isfile(output_file)
    
    fieldnames = ['Timestamp', 'Email ID', 'Label', 'Reason', 'Date', 'Company Name', 'Job Title', 'Location', 'Status', 'Metadata', 'Comment']
    try:
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(failures)
        
        # Provide clear feedback in the terminal
        absolute_path = os.path.abspath(output_file)
        print(f"\n📝 Verification log updated. See details in: {absolute_path}")

    except Exception as e:
        print(f"Error writing failures to CSV: {e}")

def fetch_all_messages_for_label(service, label_name):
    try:
        label_results = service.users().labels().list(userId='me').execute().get('labels', [])
        target_label_id = next((l['id'] for l in label_results if l['name'].lower() == label_name.lower()), None)
        if not target_label_id:
            print(f"Warning: Label '{label_name}' not found.")
            return []
        
        messages = []
        page_token = None
        while True:
            results = service.users().messages().list(userId='me', labelIds=[target_label_id], pageToken=page_token).execute()
            messages.extend(results.get('messages', []))
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        return messages
    except HttpError as error:
        print(f"HTTP error fetching messages for '{label_name}': {error}")
        return []

def get_full_message(service, msg_id):
    try:
        msg_full = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        raw = base64.urlsafe_b64decode(msg_full['raw'].encode('ASCII'))
        return email.message_from_bytes(raw, policy=policy.default)
    except HttpError as error:
        print(f"HTTP error fetching message ID {msg_id}: {error}")
        return None 