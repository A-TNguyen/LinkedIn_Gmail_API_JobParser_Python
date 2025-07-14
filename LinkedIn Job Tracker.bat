@echo off
title LinkedIn Job Tracker
echo.
echo ===============================================
echo    LinkedIn Job Application Tracker
echo ===============================================
echo.
echo Starting the application...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
)

REM Run the GUI application (no console window)
python "launchers\run_gui.pyw"

REM If that fails, try with console
if %errorlevel% neq 0 (
    echo.
    echo Error: Could not start the application without console.
    echo Trying with console window...
    python "launchers\run_gui.py"
)

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Error: Could not start the application.
    echo Please check that Python is installed and requirements are met.
    echo.
    pause
) 