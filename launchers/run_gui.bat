@echo off
title LinkedIn Job Application Tracker
echo Starting LinkedIn Job Application Tracker GUI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the GUI
python "%~dp0run_gui.py"

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Check the message above.
    pause
) 