# LinkedIn Job Application Tracker Documentation

## Overview

This documentation provides detailed information about the LinkedIn Job Application Tracker's architecture, components, and implementation details.

## Architecture

### Core Components

1. **Authentication Module** (`src/utils/auth.py`)
   - Handles Gmail API authentication
   - Manages OAuth2 credentials
   - Provides service object for Gmail API interactions

2. **Email Utilities** (`src/utils/email_utils.py`)
   - Processes Gmail API responses
   - Parses email content (plain text and HTML)
   - Extracts job application information

3. **LinkedIn Parser** (`src/parsers/linkedin_parser.py`)
   - Processes LinkedIn-specific email formats
   - Manages application status updates
   - Handles data consolidation

4. **Main Application** (`src/main.py`)
   - Orchestrates the entire process
   - Manages data flow between components
   - Handles error logging and reporting

## Detailed Component Documentation

### 1. Authentication Module

```python
def authenticate():
    """Authenticate with Gmail API using stored credentials."""
    creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)
```

**Purpose**: Manages Gmail API authentication and service creation.

**Key Features**:
- OAuth2 token management
- Automatic token refresh
- Service object creation

### 2. Email Utilities

#### Gmail API Response Processing

```python
def extract_body(payload: Dict) -> str:
    """Extract and decode email body from Gmail API payload."""
```

**Purpose**: Processes raw Gmail API responses.

**Key Features**:
- Base64 decoding
- MIME type handling
- Error handling for malformed data

#### Email Message Parsing

```python
def get_plain_text_body(msg: EmailMessage) -> str:
    """Extract plain text content from an EmailMessage object."""
```

**Purpose**: Extracts content from parsed email messages.

**Key Features**:
- Multipart message handling
- Character encoding management
- Content type detection

### 3. LinkedIn Parser

#### Email Processing

```python
def parse_messages(service, label_name: str) -> List[Dict]:
    """Parse messages for a specific label and extract relevant information."""
```

**Purpose**: Processes LinkedIn job application emails.

**Key Features**:
- Label-based processing
- Status tracking
- Data extraction

#### Data Management

```python
def save_to_excel(applied_rows: List[Dict], viewed_rows: List[Dict], rejected_rows: List[Dict]):
    """Save parsed data to Excel file with separate sheets for each status."""
```

**Purpose**: Manages data storage and organization.

**Key Features**:
- Multi-sheet Excel export
- Data deduplication
- Status prioritization

## Email Processing Details

### 1. Applied Status

**Email Format**:
```
Subject: Your application was sent to [Company]
Body:
[Job Title]
[Company Name]
[Location]
```

**Processing**:
- Extracts company name from subject
- Parses job title and location from body
- Creates new application entry

### 2. Viewed Status

**Email Format**:
```
Subject: Your application was viewed by [Company]
Body: HTML content with job details
```

**Processing**:
- Updates existing application status
- Maintains previous details
- Adds view timestamp

### 3. Rejected Status

**Email Format**:
```
Subject: Your application to [Position] at [Company]
Body: HTML content with job details
```

**Processing**:
- Updates application status
- Maintains application history
- Records rejection date

## Data Structure

### Application Entry

```python
{
    "Company Name": str,
    "Job Title": str,
    "Status": str,  # "Applied", "Viewed", or "Rejected"
    "Date": str,    # MM/DD/YYYY format
    "Location": str,
    "Metadata Subject": str,
    "Comment": str
}
```

### Status Priority

1. Rejected (highest)
2. Viewed
3. Applied (lowest)

## Error Handling

### 1. Authentication Errors

- Invalid credentials
- Expired tokens
- API quota exceeded

### 2. Parsing Errors

- Malformed email content
- Missing required fields
- Unexpected email format

### 3. Data Export Errors

- File permission issues
- Disk space limitations
- Excel file conflicts

## Logging

### Log File Structure

```
logs/job_application_logs.txt
```

**Format**:
```
[Timestamp] [Level] Message
```

**Levels**:
- INFO: Normal operation
- WARNING: Non-critical issues
- ERROR: Critical failures

## Best Practices

1. **Security**
   - Keep credentials in `config/` directory
   - Never commit sensitive files
   - Regular token rotation

2. **Data Management**
   - Regular backups of Excel file
   - Archive old logs
   - Monitor disk space

3. **Error Handling**
   - Check logs regularly
   - Monitor API quotas
   - Verify email formats

## API Limits

- Gmail API: 1,000,000,000 quota units per day
- Rate limits apply to:
  - Message listing
  - Message retrieval
  - Batch operations

## Troubleshooting Guide

### Common Issues

1. **Authentication Failures**
   ```bash
   # Solution: Delete token and re-authenticate
   rm config/token.json
   python src/main.py
   ```

2. **Parsing Errors**
   ```bash
   # Check logs for details
   cat logs/job_application_logs.txt
   ```

3. **Export Issues**
   ```bash
   # Ensure Excel is closed
   # Check file permissions
   ls -l data/processed/
   ```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Document functions

2. **Testing**
   - Unit tests for utilities
   - Integration tests for parsing
   - Mock Gmail API responses

3. **Version Control**
   - Feature branches
   - Meaningful commits
   - Pull request reviews

## Future Improvements

1. **Planned Features**
   - Email notification system
   - Web dashboard
   - API endpoint

2. **Potential Enhancements**
   - Multiple email account support
   - Custom status types
   - Data visualization

## Support

For technical support:
1. Check the troubleshooting guide
2. Review the logs
3. Create a GitHub issue

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details 