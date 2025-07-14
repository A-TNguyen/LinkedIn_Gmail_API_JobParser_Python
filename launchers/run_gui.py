#!/usr/bin/env python3
"""
GUI Launcher for LinkedIn Job Application Tracker

This script launches the graphical user interface for the EmailJobParser.
Run this file to start the GUI application.
"""

import sys
import os

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level from launchers
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

try:
    from gui.main_window import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Import Error", f"Failed to import GUI components:\n{e}")
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"An error occurred:\n{e}") 