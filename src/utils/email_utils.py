"""
Gmail API Email Utilities

This module provides utilities for working with Gmail API responses and email parsing.
It handles both raw Gmail API responses and parsed email messages.

Key Components:
1. Gmail API Response Processing
   - extract_body: Processes raw Gmail API payload
   - parse_internal_date: Converts Gmail's internal timestamp

2. Email Message Parsing
   - get_plain_text_body: Extracts plain text from EmailMessage
   - get_html_body: Extracts HTML content from EmailMessage

3. LinkedIn-specific Parsing
   - parse_applied_email_body: Parses LinkedIn application emails
   - parse_html_for_job_info: Extracts job details from LinkedIn HTML
   - extract_applied_info: Simplified LinkedIn application info extraction
"""

import base64
import re
from datetime import datetime
from typing import Dict, Tuple
from email.message import EmailMessage

# === Gmail API Response Processing ===

def parse_internal_date(internal_date: str) -> str:
    """Convert Gmail internal date to YYYY-MM-DD format, filtering out dates before 2004."""
    try:
        dt = datetime.fromtimestamp(int(internal_date) / 1000)
        # Check if year is 2004 or later
        if dt.year < 2004:
            return ""
        return dt.strftime('%Y-%m-%d')
    except:
        return ""

def extract_body(payload: Dict) -> str:
    """
    Extract and decode email body from Gmail API payload.
    
    Args:
        payload (Dict): Raw Gmail API message payload
    
    Returns:
        str: Decoded email body content
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    elif 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return ''

# === Email Message Parsing ===

def get_plain_text_body(msg: EmailMessage) -> str:
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            return msg.get_payload(decode=True).decode('latin-1', errors='ignore')
    return ""

def get_html_body(msg: EmailMessage) -> str:
    """Extract HTML body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/html' and 'attachment' not in cdispo:
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    else:
        ctype = msg.get_content_type()
        if ctype == 'text/html':
            try:
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                return msg.get_payload(decode=True).decode('latin-1', errors='ignore')
    return ""

# === LinkedIn-specific Parsing ===

def parse_applied_email_body(plain_text_body: str) -> dict:
    """Extract job info from Applied email body."""
    job_title = ""
    company_name = ""
    location = ""

    lines = plain_text_body.splitlines()
    
    start_index = -1
    for i, line in enumerate(lines):
        if "Your application was sent to" in line:
            start_index = i
            break
    
    if start_index == -1:
        raise ValueError("Anchor phrase 'Your application was sent to' not found in plain text body.")

    # Find the next 3 non-empty lines after the anchor
    relevant_lines = []
    current_index = start_index + 1
    while len(relevant_lines) < 3 and current_index < len(lines):
        line = lines[current_index].strip()
        if line:
            relevant_lines.append(line)
        current_index += 1
    
    if len(relevant_lines) >= 3:
        job_title = relevant_lines[0].strip()
        company_name = relevant_lines[1].strip()
        location = relevant_lines[2].strip()

    if not job_title:
        raise ValueError("Job Title not found or is empty after anchor phrase.")
    if not company_name:
        raise ValueError("Company Name not found or is empty after anchor phrase.")
    if not location:
        raise ValueError("Location not found or is empty after anchor phrase.")

    return {
        "Job Title": job_title,
        "Company Name": company_name,
        "Location": location
    }

def parse_html_for_job_info(html_content: str) -> dict:
    """Extract job info from HTML content."""
    job_title = ""
    company_name = ""
    location = ""

    # Regex for Job Title
    job_title_match = re.search(
        r'line-height:\s*1\.25;\s*color:\s*#0a66c2;">\s*(.*?)(?:</a>|</td)',
        html_content, re.DOTALL | re.IGNORECASE
    )
    if job_title_match:
        job_title = job_title_match.group(1).strip()
        job_title = job_title.replace('&amp;', '&').replace('&nbsp;', ' ').replace('=C2=A0', ' ')
        job_title = re.sub(r'\s+', ' ', job_title).strip()

    # Regex for Company Name and Location
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

    return {
        "Job Title": job_title,
        "Company Name": company_name,
        "Location": location
    }

def extract_applied_info(body: str) -> Tuple[str, str, str]:
    """
    Simplified version of parse_applied_email_body that returns a tuple.
    Used for quick extraction of basic application information.
    
    Args:
        body (str): Email body content
    
    Returns:
        Tuple[str, str, str]: (company, title, location)
    """
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    company, title, location = '', '', ''
    for i, line in enumerate(lines):
        if line.lower().startswith("your application was sent to"):
            company = line.split("to")[-1].strip()
            title = lines[i + 1] if i + 1 < len(lines) else ''
            location = lines[i + 2] if i + 2 < len(lines) else ''
            if 'remote' in location.lower():
                location += ' (Remote)'
            break
    return company, title, location 