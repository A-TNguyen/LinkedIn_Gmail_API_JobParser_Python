# LinkedIn Job Application Tracker

A Python application that automatically tracks your LinkedIn job application statuses by parsing Gmail notifications. This tool helps you maintain a clear overview of your job search progress by organizing application statuses (Applied, Viewed, Rejected) into an Excel spreadsheet.

## Features

- 🔄 Automatic Gmail API integration
- 📧 Parses LinkedIn job application emails
- 📊 Tracks multiple application statuses:
  - Applied
  - Viewed
  - Rejected
- 📈 Exports data to organized Excel sheets
- 🔍 Handles both plain text and HTML email formats
- 📝 Detailed logging for debugging
- 🔒 Secure credential management

## Prerequisites

- Python 3.7 or higher
- Google Cloud Project with Gmail API enabled
- A Gmail account with the following label structure set up:
    - A parent label named `LinkedIn`.
    - Nested under `LinkedIn`, three child labels:
        - `Applied`
        - `Viewed`
        - `Rejected`

This structure is crucial for the application to find and parse your job application emails correctly. When you receive a notification from LinkedIn, apply the corresponding label (e.g., `LinkedIn/Applied`).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-job-tracker.git
   cd linkedin-job-tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file
5. Rename the downloaded file to `credentials.json`
6. Place `credentials.json` in the `config/` directory

## Usage

1. First-time setup:
   ```bash
   python src/main.py
   ```
   - This will open a browser window for Google authentication
   - Grant the necessary permissions
   - A `token.json` file will be created in the `config/` directory

2. Regular usage:
   ```bash
   python src/main.py
   ```
   - The script will:
     - Fetch emails from your Gmail account
     - Parse LinkedIn job application notifications
     - Update the Excel spreadsheet
     - Generate logs in the `logs/` directory

3. Output:
   - Excel file: `data/processed/LinkedIn_Job_Status_Parsed.xlsx`
   - Logs: `logs/job_application_logs.txt`

## Project Structure

```
linkedin-job-tracker/
├── config/                 # Configuration files
│   ├── credentials.json    # Google API credentials
│   └── token.json         # Generated auth token
├── src/                   # Source code
│   ├── parsers/          # Email parsing modules
│   │   ├── __init__.py
│   │   └── linkedin_parser.py
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── email_utils.py
│   ├── __init__.py
│   └── main.py           # Main application
├── data/                  # Data directory
│   ├── raw/              # Raw email data
│   └── processed/        # Processed data
├── logs/                  # Application logs
├── tests/                # Test files
├── .gitignore            # Git ignore file
├── requirements.txt       # Project dependencies
└── README.md             # This file
```

## Email Processing

The application processes three types of LinkedIn emails:

1. **Applied**
   - Subject: "Your application was sent to [Company]"
   - Extracts: Job Title, Company Name, Location

2. **Viewed**
   - Subject: "Your application was viewed by [Company]"
   - Updates status and maintains existing details

3. **Rejected**
   - Subject: "Your application to [Position] at [Company]"
   - Updates status and maintains existing details

## Security

- Never commit `credentials.json` or `token.json`
- Keep your Google API credentials secure
- The `.gitignore` file is configured to exclude sensitive files
- All sensitive data is stored in the `config/` directory

## Troubleshooting

1. **Authentication Issues**
   - Delete `token.json` and run the script again
   - Ensure `credentials.json` is in the correct location
   - Check Google Cloud Console for API status

2. **Email Parsing Issues**
   - Check `logs/job_application_logs.txt` for detailed error messages
   - Verify email format matches expected patterns
   - Ensure Gmail labels are correctly set

3. **Data Export Issues**
   - Check file permissions in `data/processed/`
   - Ensure Excel is not open when running the script
   - Verify sufficient disk space

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## How to Add or Modify Email Labels

This parser is designed to be easily configurable without changing any Python code. You can control which Gmail labels are processed by editing a single file.

**File to Edit:** `config/label_config.json`

### How It Works

The `label_config.json` file contains a list of "label objects". Each object tells the parser:
1.  Which Gmail label to look for (`label_name`).
2.  What application `status` to assign to emails with that label.
3.  The `priority` of that status (higher numbers override lower ones).
4.  Which `parser_type` to use to understand the email's content.

### Example: Adding a "Phone Screen" Label

Imagine you create a new Gmail label called `LinkedIn/PhoneScreen` for emails about scheduling a phone interview. To make the parser recognize this, you would add a new object to the `config/label_config.json` file:

```json
[
  {
    "label_name": "LinkedIn/Applied",
    "status": "Applied",
    "priority": 1,
    "parser_type": "applied"
  },
  {
    "label_name": "LinkedIn/Viewed",
    "status": "Viewed",
    "priority": 2,
    "parser_type": "viewed_rejected"
  },
  {
    "label_name": "LinkedIn/Rejected",
    "status": "Rejected",
    "priority": 3,
    "parser_type": "viewed_rejected"
  },
  {
    "label_name": "LinkedIn/PhoneScreen",
    "status": "Phone Screen",
    "priority": 4,
    "parser_type": "viewed_rejected"
  }
]
```

**Explanation of the new entry:**
-   `"label_name": "LinkedIn/PhoneScreen"`: The exact name of your new label in Gmail.
-   `"status": "Phone Screen"`: The text that will appear in the "Status" column of your CSV report.
-   `"priority": 4`: We give it a high priority so it will override "Viewed" or "Applied".
-   `"parser_type": "viewed_rejected"`: We are reusing the existing parser for "Viewed" and "Rejected" emails, as they are likely to have a similar HTML structure where the company and job title can be found. If you had a completely new email format, a new parser function would need to be added to the script. 