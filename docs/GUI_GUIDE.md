# GUI User Guide

## Overview

The LinkedIn Job Application Tracker GUI provides an intuitive interface for processing your job application emails without needing to use command-line arguments.

## Starting the GUI

### Windows
- **Option 1 (Recommended):** Double-click `run_gui_no_console.bat` - Launches without any console window
- **Option 2:** Double-click `run_gui.pyw` - Python GUI launcher without console
- **Option 3:** Double-click `run_gui.bat` - Standard launcher with console
- **Option 4:** Open Command Prompt and run `python run_gui.py`

### Mac/Linux
- Open Terminal and run `python run_gui.py`

## GUI Features

### Resizable Interface
- The GUI is **fully resizable** - drag corners or edges to resize
- **Minimum size**: 700×800 pixels to maintain usability
- **All components scale** dynamically with window size:
  - 📱 **Buttons**: Maintain proper spacing and expand with window
  - 📊 **Progress bar**: Stretches to fill available width
  - 📺 **Console output**: Main expanding area - grows/shrinks with window
  - 📋 **All text areas**: Scale proportionally with window size

### Dynamic Console Output
- **Main expanding area** - takes up most of the additional space when resizing
- **Minimum size**: 10 lines × 50 characters for readability
- **Scales up**: Console area grows significantly when window is enlarged
- **Real-time processing updates** with color-coded messages:
  - 🟢 **Green**: Success messages
  - 🔴 **Red**: Error messages  
  - 🟡 **Yellow**: Warning messages
  - 🔵 **Blue**: Information messages
- **Auto-scrolling** to show the latest output
- **Clear button** to reset the console output

### Responsive Layout
- **Smart grid system** - all components use proper weights for scaling
- **Centered buttons** - action buttons stay centered regardless of window width
- **Flexible date selection** - radio buttons expand to fill available space
- **Scalable progress indicators** - stretch to match window width
- **Professional appearance** at any window size

## GUI Components

### 1. Date Range Selection

The GUI provides several easy ways to select which emails to process:

**Quick Selection Buttons:**
- **All Time** - Process all emails (default)
- **Last 24 Hours** - Process emails from the last day
- **Last Week** - Process emails from the last 7 days
- **Last Month** - Process emails from the last 30 days
- **Last 3 Months** - Process emails from the last 90 days
- **Last Year** - Process emails from the last 365 days

**Custom Date Range:**
- Select "Custom Date Range" radio button
- Enter start date in "From" field (YYYY-MM-DD format)
- Enter end date in "To" field (YYYY-MM-DD format)
- Example: From `2024-01-01` To `2024-12-31`

### 2. Action Buttons

The GUI provides several action buttons for managing your email processing:

**🚀 Start Processing**
- Begins processing emails with the selected date range
- Button becomes disabled during processing
- Shows real-time progress and updates

**⏹ Stop**
- Requests to stop the current processing operation
- Only enabled during processing
- Note: Stopping depends on the current operation state

**📦 Archive Files**
- Archives processed files into organized folders
- Creates separate directories for different file types:
  - `data/archive/job_applications/` - Job application status files
  - `data/archive/failed_verifications/` - Failed verification logs
  - `data/archive/logs/` - Processing logs (copied, not moved)
- Shows detailed archive summary in console output
- Moves files from `data/processed/` to `data/archive/` and deletes originals
- New processed files always go to `data/processed/` first

**📁 Open Output Folder**
- Opens the `data/processed/` folder in your system file explorer
- Works cross-platform (Windows, macOS, Linux)
- Creates the folder if it doesn't exist

**📄 Open Latest File**
- Opens the most recently created output file
- Only enabled after successful processing
- Uses system default application for CSV files

### 3. Progress Section

- **Status Text** - Shows current operation (e.g., "Authenticating...", "Processing emails...")
- **Email Count** - Shows number of emails found and being processed
- **Progress Bar** - Visual indicator with actual progress percentage
- **Progress Percentage** - Shows exact completion percentage

### 4. Output Log

- **Real-time Console Output** - Shows detailed output of what's happening (same as command-line)
- **Timestamps** - Each log entry includes time stamp
- **Scrollable** - Automatically scrolls to show latest entries
- **Progress Parsing** - Automatically extracts progress information from console output

### 5. Status Bar

- Shows current application status at the bottom

## Step-by-Step Usage

1. **Launch the GUI**
   - Run `python run_gui.py` or double-click `run_gui.bat`

2. **Select Date Range**
   - Choose one of the quick options (recommended for most users)
   - Or select "Custom Date Range" and enter specific dates

3. **Start Processing**
   - Click "🚀 Start Processing"
   - The application will authenticate with Gmail (first time only)
   - Watch the progress in the log window

4. **Monitor Progress**
   - Real-time updates appear in the Output Log
   - Progress bar shows activity
   - Status updates appear at the bottom

5. **Completion**
   - Success message appears when complete
   - Progress bar shows 100% completion
   - "Open Latest File" button becomes available
   - Output files are saved in `data/processed/`
   - Log shows summary of processed emails with file paths

## First-Time Setup

When you run the application for the first time:

1. **Authentication Required**
   - A browser window will open
   - Sign in to your Google account
   - Grant permissions to access Gmail
   - The GUI will show "Authentication successful"

2. **Credentials Saved**
   - Your authentication token is saved for future use
   - No need to re-authenticate unless token expires

## File Organization

### Output Files
All processed files are saved in the `data/` directory structure with timestamped names:
- **Job Application Status**: `data/processed/job_application_status_{range}_{timestamp}.csv`
- **Failed Verifications**: `data/processed/failed_verifications_{timestamp}.csv`
- **Processing Logs**: `data/logs/parser_run.log`

### Archive Structure
When you use the **📦 Archive Files** button, files are organized into:

```
data/archive/
├── job_applications/
│   ├── job_application_status_last_week_20240115_143022.csv
│   ├── job_application_status_all_time_20240114_091530.csv
│   └── job_application_status_custom_2024-01-01_to_2024-01-31_20240113_164500.csv
├── failed_verifications/
│   ├── failed_verifications_20240115_143022.csv
│   ├── failed_verifications_20240114_091530.csv
│   └── failed_verifications_20240113_164500.csv
└── logs/
    ├── 20240115_143022_parser_run.log
    ├── 20240114_091530_parser_run.log
    └── 20240113_164500_parser_run.log
```

### Archive Benefits
- **Organized Storage**: Files are categorized by type for easy access
- **Clean Workspace**: Keeps the main processed directory uncluttered
- **Historical Records**: Maintains chronological organization of all processing runs
- **Safe Operation**: Log files are copied (not moved) to preserve current logs

## Common Usage Patterns

### Daily Check
- Select "Last 24 Hours"
- Click "Start Processing"
- Quick way to check new applications

### Weekly Review
- Select "Last Week"
- Good for regular weekly updates

### Monthly Report
- Select "Last Month"
- Comprehensive monthly review

### Initial Setup
- Select "All Time"
- Process all historical emails

### Specific Period
- Use "Custom Date Range"
- Enter exact start and end dates

## Troubleshooting

### GUI Won't Start
- Check Python version: `python --version` (needs 3.7+)
- Try running from terminal: `python run_gui.py`
- Check for error messages in terminal

### Authentication Issues
- Delete `config/token.json`
- Restart the GUI
- Re-authenticate when prompted

### Processing Errors
- Check the Output Log for specific error messages
- Verify Gmail labels exist (LinkedIn/Applied, LinkedIn/Viewed, LinkedIn/Rejected)
- Ensure internet connection is stable

### Date Range Issues
- Use YYYY-MM-DD format for custom dates
- Ensure start date is before end date
- Don't use future dates

## Tips for Best Results

1. **Use Recent Date Ranges** - Processing fewer emails is faster
2. **Check Logs** - Always review the output log for any issues
3. **Regular Processing** - Run weekly or monthly for best results
4. **Backup Data** - The application automatically archives previous results

## Keyboard Shortcuts

- **Enter** - Activates the Start Processing button when focused
- **Escape** - Closes dialog boxes
- **Ctrl+A** - Select all text in log window
- **Ctrl+C** - Copy selected text from log window 