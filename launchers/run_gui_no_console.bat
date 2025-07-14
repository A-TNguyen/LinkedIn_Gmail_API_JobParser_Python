@echo off
REM LinkedIn Job Application Tracker GUI Launcher (No Console)
REM Double-click this file to launch the GUI without any console window

cd /d "%~dp0"

REM Try to use pythonw.exe (Windows Python without console)
if exist "%~dp0..\\.venv\\Scripts\\pythonw.exe" (
    "%~dp0..\\.venv\\Scripts\\pythonw.exe" "%~dp0run_gui.pyw"
) else if exist "%~dp0..\\.venv\\Scripts\\python.exe" (
    "%~dp0..\\.venv\\Scripts\\python.exe" "%~dp0run_gui.pyw"
) else (
    REM Fall back to system Python
    pythonw "%~dp0run_gui.pyw" 2>nul || python "%~dp0run_gui.pyw"
)

REM If all else fails, show error
if errorlevel 1 (
    echo Error: Could not find Python interpreter
    echo Please ensure Python is installed and virtual environment is activated
    pause
) 