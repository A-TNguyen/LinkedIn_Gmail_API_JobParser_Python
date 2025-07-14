# LinkedIn Job Application Tracker

A Python application that automatically tracks your LinkedIn job application statuses by parsing Gmail notifications. This tool helps you maintain a clear overview of your job search progress by organizing application statuses (Applied, Viewed, Rejected) into an Excel spreadsheet.

<img width="900" height="1013" alt="image" src="https://github.com/user-attachments/assets/6091c53a-b2ab-4da9-9dca-1eb042df55a2" />


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

## Quick Start

### 🚀 **Easy Launch (Windows)**
1. **Double-click `LinkedIn Job Tracker.bat`** in the project root
2. The application will start automatically!

### 📋 **First-Time Setup**
1. Download or clone this repository
2. Install Python 3.7+ if not already installed
3. Install dependencies: `pip install -r requirements.txt`
4. Set up Gmail API credentials (see setup guide in the app)
5. Launch the application using the main launcher

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

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google API credentials** (see detailed setup below)

3. **Run the application:**
   - **GUI (Recommended):** Double-click `run_gui.bat` (Windows) or run `python run_gui.py`
   - **Command Line:** Run `python src/main.py`

4. **First run:** Authenticate with Google when prompted

5. **Select date range** and click "Start Processing"

That's it! Your job application data will be processed and saved to Excel.

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

### 🎯 **Graphical Interface (Recommended)**

**Main Launcher (Windows):**
- **Double-click `LinkedIn Job Tracker.bat`** in the project root

**Alternative Launchers:**
- `launchers/run_gui.py` - Python script with console output
- `launchers/run_gui.pyw` - Python script without console (silent)
- `launchers/run_gui.bat` - Windows batch file with console
- `launchers/run_gui_no_console.bat` - Windows batch file without console

**Mac/Linux Users:**
- Run: `python launchers/run_gui.py`

The GUI provides:
- ✅ **Easy date range selection** with buttons (Last 24 Hours, Last Week, etc.)
- ✅ **Custom date range picker** for specific periods
- ✅ **Real-time progress tracking** with actual email counts and percentages
- ✅ **Live console output** showing exactly what's happening
- ✅ **Built-in API setup guide** with step-by-step instructions
- ✅ **Help system** with documentation viewer
- ✅ **File management and archiving** tools
- ✅ **Quick file access** with "Open Output Folder" and "Open Latest File" buttons
- ✅ **Success/error notifications** with clear messages
- ✅ **No command-line knowledge required**

### 💻 Command Line Interface

For advanced users or automation:

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

### Date Range Filtering

You can filter emails by date range to process only recent emails:

```bash
# Process emails from the last 24 hours
python src/main.py --date-range 24h

# Process emails from the last week
python src/main.py --date-range 7d

# Process emails from the last month
python src/main.py --date-range 30d

# Process emails from the last 3 months
python src/main.py --date-range 90d

# Process emails from the last year
python src/main.py --date-range 1y

# Process emails from a custom date range
python src/main.py --date-range 2024-01-01:2024-12-31

# List all available date range options
python src/main.py --list-ranges
```

**Available Date Ranges:**
- `all` - All emails (default)
- `24h` or `1d` - Last 24 hours
- `7d` or `1w` - Last 7 days
- `30d` or `1m` - Last 30 days
- `90d` or `3m` - Last 90 days
- `1y` - Last year
- `YYYY-MM-DD:YYYY-MM-DD` - Custom date range

### Command Line Options

```bash
python src/main.py [OPTIONS]

Options:
  -d, --date-range TEXT   Date range to process (default: all)
  -l, --list-ranges      List available date ranges and exit
  -h, --help             Show help message and exit
```

### Output Files

The application creates separate files for each date range with timestamps to avoid overwriting:

**Main Output:**
- `data/processed/job_application_status_{date_range}_{timestamp}.csv`

**Examples:**
- `job_application_status_all_time_20250113_143022.csv`
- `job_application_status_last_week_20250113_143022.csv`
- `job_application_status_custom_2024-01-01_to_2024-12-31_20250113_143022.csv`

**Other Files:**
- **Failure logs:** `data/processed/failed_verifications_{timestamp}.csv` (single file with source info)
- **Application logs:** `logs/parser_run.log`

This naming system allows you to:
- Keep results from different date ranges separate
- Track when each run was performed
- Compare results across different time periods
- Never lose previous results due to overwriting

## Project Structure

```
linkedin-job-tracker/
├── config/                 # Configuration files
│   ├── credentials.json    # Google API credentials
│   └── token.json         # Generated auth token
├── src/                   # Source code
│   ├── gui/              # Graphical user interface
│   │   └── main_window.py # Main GUI application
│   ├── parsers/          # Email parsing modules
│   │   ├── __init__.py
│   │   └── linkedin/     # LinkedIn-specific parsers
│   │       ├── __init__.py
│   │       ├── email_parsers.py
│   │       └── processor.py
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py       # Gmail authentication
│   │   ├── date_utils.py # Date range utilities
│   │   ├── email_utils.py # Email parsing utilities
│   │   ├── file_utils.py # File operations
│   │   └── gmail_utils.py # Gmail API utilities
│   ├── __init__.py
│   └── main.py           # Command-line application
├── data/                  # Data directory
│   ├── raw/              # Raw email data
│   └── processed/        # Processed data
├── logs/                  # Application logs
├── run_gui.py            # GUI launcher (cross-platform)
├── run_gui.bat           # GUI launcher (Windows)
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

### Sensitive Files Protection

The following files contain sensitive information and are automatically excluded from version control:

**Authentication Files:**
- `credentials.json` - Google API credentials
- `token.json` - OAuth access tokens
- `client_secret*.json` - Downloaded OAuth credentials
- `.env` - Environment variables with API keys

**Generated Data Files:**
- `LinkedIn_Job_Status_Parsed.xlsx` - Contains personal job application data
- `failed_verifications.csv` - May contain email content
- `parser_run.log` - Application logs with potential sensitive info
- `job_application_logs.txt` - Detailed processing logs

**Directories with Sensitive Content:**
- `config/` - All configuration files
- `src/logs/` - Application log files
- `src/data/` - Raw and processed email data
- `archive/` - Archived sensitive files

### Security Best Practices

- **Never commit sensitive files** - The `.gitignore` is configured to protect these automatically
- **Keep credentials secure** - Store in the `config/` directory only
- **Regular maintenance** - Rotate API credentials periodically
- **Local development** - Use different credentials for development/production
- **File permissions** - Ensure sensitive files have restricted access (600 permissions on Unix systems)

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

4. **Date Range Issues**
   - Use `--list-ranges` to see available options
   - Ensure custom date ranges use YYYY-MM-DD format
   - Check that start date is before end date in custom ranges
   - Verify dates are not in the future

5. **GUI Issues**
   - If GUI won't start: Check Python version (3.7+ required)
   - If GUI crashes: Check the console output for error messages
   - If buttons don't work: Try running `python run_gui.py` from terminal
   - If authentication fails: Delete `config/token.json` and try again

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
