import re
import email

def get_plain_text_body(msg: email.message.Message) -> str:
    """
    Parses an email.message.Message object and returns its plain text body.

    Args:
        msg: The email message object to parse.

    Returns:
        The plain text content of the email as a string.
    """
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

def get_html_body(msg: email.message.Message) -> str:
    """
    Parses an email.message.Message object and returns its HTML body.

    Args:
        msg: The email message object to parse.

    Returns:
        The HTML content of the email as a string.
    """
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
    """
    Parses the plain text body of a 'LinkedIn/Applied' email to extract job details.

    Args:
        plain_text_body: The plain text content of the 'Applied' email.

    Returns:
        A dictionary containing the parsed "Job Title", "Company Name", and "Location".
    
    Raises:
        ValueError: If any of the mandatory fields are missing.
    """
    job_title, company_name, location = "", "", ""
    lines = plain_text_body.splitlines()
    try:
        start_index = next(i for i, line in enumerate(lines) if "Your application was sent to" in line)
        relevant_lines = [line.strip() for line in lines[start_index + 1:] if line.strip()]
        if len(relevant_lines) >= 3:
            job_title, company_name, location = relevant_lines[0], relevant_lines[1], relevant_lines[2]
    except (StopIteration, IndexError):
        pass

    if not all([job_title, company_name, location]):
        missing = [f for f, v in [("Job Title", job_title), ("Company Name", company_name), ("Location", location)] if not v]
        raise ValueError(f"Could not parse required fields. Missing: {', '.join(missing)}")
        
    return {"Job Title": job_title, "Company Name": company_name, "Location": location}

def parse_viewed_rejected_info(html_content: str, subject: str) -> dict:
    """
    Parses 'Viewed' or 'Rejected' emails to extract job details, using HTML and subject lines.

    Args:
        html_content: The HTML body of the email.
        subject: The subject line of the email.

    Returns:
        A dictionary containing the parsed job details and an "error" key.
    """
    job_title, company_name, location = "", "", ""
    error_message = None
    
    company_location_match = re.search(r'<p[^>]*?>\s*([^<]+?)\s*·\s*(.*?)\s*</p>', html_content, re.IGNORECASE)
    if company_location_match:
        company_name = company_location_match.group(1).strip()
        location = company_location_match.group(2).strip()
    
    job_title_match = re.search(r'color:\s*#0a66c2;">\s*([^<]+?)\s*<', html_content, re.IGNORECASE)
    if job_title_match:
        job_title = job_title_match.group(1).strip()
        
    if 'viewed by' in subject.lower():
        match = re.search(r'Your application was viewed by\s+(.*)', subject, re.IGNORECASE)
        if match and not company_name: company_name = match.group(1).strip()
    
    if 'application to' in subject.lower() and 'at' in subject.lower():
         match = re.search(r'Your application to\s+(.*?)\s+at\s+(.*)', subject, re.IGNORECASE)
         if match:
             if not job_title: job_title = match.group(1).strip()
             if not company_name: company_name = match.group(2).strip()
    
    if company_name: company_name = company_name.replace('&amp;', '&').strip()
    if job_title: job_title = job_title.replace('&amp;', '&').strip()
    if location: location = location.replace('&amp;', '&').strip()

    if not company_name:
        error_message = "Critical parse failure: Could not determine Company Name from HTML or Subject."

    return {"Job Title": job_title, "Company Name": company_name, "Location": location, "error": error_message}

def parse_date_header(date_string: str) -> dict:
    """
    Parses a date string from an email header into 'YYYY-MM-DD' format.
    
    Args:
        date_string: The raw date string from the email header.

    Returns:
        A formatted date string ('YYYY-MM-DD').
    """
    from dateutil import parser as date_parser
    if not date_string: return ""
    try:
        return date_parser.parse(date_string).strftime('%Y-%m-%d')
    except (date_parser.ParserError, TypeError):
        return ""

def generate_comment(subject: str) -> str:
    """
    Generates a simple, consistent comment based on the email's subject line.

    Args:
        subject: The subject line of the email.

    Returns:
        A formatted comment string.
    """
    return f"Email regarding: {subject}" if subject else "No subject found." 