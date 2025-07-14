# GUI Launchers

This directory contains different ways to launch the LinkedIn Job Application Tracker GUI.

## Quick Start

**For most users**: Double-click `LinkedIn Job Tracker.bat` in the main project folder.

## Launcher Options

### 1. `run_gui.py` 
- **Python script launcher**
- Shows console window with debug information
- Use if you want to see detailed output or troubleshoot issues

### 2. `run_gui.pyw`
- **Python script launcher (no console)**
- Runs silently without showing a console window
- Clean user experience, recommended for regular use

### 3. `run_gui.bat`
- **Windows batch file**
- Shows console window with status messages
- Automatically handles Python path and virtual environment
- Good for troubleshooting

### 4. `run_gui_no_console.bat`
- **Windows batch file (no console)**
- Runs silently without showing a console window
- Tries different Python interpreters automatically
- Clean user experience

## Usage

1. **Double-click any launcher** to start the application
2. **Or run from command line:**
   ```bash
   # From the launchers directory
   python run_gui.py
   # or
   python run_gui.pyw
   ```

## Troubleshooting

- If launchers don't work, ensure Python 3.7+ is installed
- Make sure you've installed requirements: `pip install -r requirements.txt`
- Try `run_gui.py` first to see any error messages
- Check that you're in the correct directory with the virtual environment

## Main Launcher

The main launcher `LinkedIn Job Tracker.bat` is located in the project root directory for easy access. It automatically:
- Activates the virtual environment if available
- Tries the no-console version first
- Falls back to console version if needed
- Shows helpful error messages 