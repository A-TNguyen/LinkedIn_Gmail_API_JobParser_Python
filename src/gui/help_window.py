#!/usr/bin/env python3
"""
Help Window System for LinkedIn Job Application Tracker

This module provides help windows for API setup guidance and documentation viewing.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import webbrowser
import subprocess
import platform
from pathlib import Path

class HelpWindow:
    """Main help window with different help sections"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("LinkedIn Job Tracker - Help")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the help window UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Job Tracker - Help Center", 
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Help sections
        sections_frame = ttk.Frame(main_frame)
        sections_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Help categories
        left_frame = ttk.LabelFrame(sections_frame, text="Help Categories", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Help buttons
        ttk.Button(left_frame, text="🔧 API Setup Guide", 
                  command=self.show_api_setup, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(left_frame, text="📖 User Documentation", 
                  command=self.show_documentation, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(left_frame, text="🎯 GUI Guide", 
                  command=self.show_gui_guide, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(left_frame, text="📁 File Naming Examples", 
                  command=self.show_file_naming, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(left_frame, text="🔍 Troubleshooting", 
                  command=self.show_troubleshooting, width=20).pack(pady=5, fill=tk.X)
        
        # Separator
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # External links
        ttk.Button(left_frame, text="🌐 Open README", 
                  command=self.open_readme, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(left_frame, text="📂 Open Docs Folder", 
                  command=self.open_docs_folder, width=20).pack(pady=5, fill=tk.X)
        
        # Right panel - Content display
        right_frame = ttk.LabelFrame(sections_frame, text="Help Content", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content display area
        self.content_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, 
                                                     font=("Consolas", 10))
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.content_text.tag_configure("heading1", font=("Helvetica", 14, "bold"), 
                                       foreground="#2c3e50")
        self.content_text.tag_configure("heading2", font=("Helvetica", 12, "bold"), 
                                       foreground="#34495e")
        self.content_text.tag_configure("code", font=("Consolas", 9), 
                                       background="#f8f9fa", foreground="#e74c3c")
        self.content_text.tag_configure("important", font=("Helvetica", 10, "bold"), 
                                       foreground="#e67e22")
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        
        # Show initial content
        self.show_welcome()
    
    def show_welcome(self):
        """Show welcome message"""
        content = """Welcome to LinkedIn Job Tracker Help Center!

Select a help category from the left panel to get started:

🔧 API Setup Guide - Step-by-step instructions for setting up Gmail API
📖 User Documentation - Complete user guide and features
🎯 GUI Guide - How to use the graphical interface
📁 File Naming Examples - Understanding output file naming
🔍 Troubleshooting - Common issues and solutions

Quick Start:
1. First, set up your Gmail API credentials using the API Setup Guide
2. Review the User Documentation to understand all features
3. Use the GUI Guide to learn the interface
4. Check File Naming Examples to understand output files

Need immediate help? Check the troubleshooting section for common issues.
"""
        self.display_content(content)
    
    def show_api_setup(self):
        """Show API setup guidance"""
        APISetupWindow(self.window)
    
    def show_documentation(self):
        """Show user documentation"""
        self.load_markdown_file("docs/DOCUMENTATION.md")
    
    def show_gui_guide(self):
        """Show GUI guide"""
        self.load_markdown_file("docs/GUI_GUIDE.md")
    
    def show_file_naming(self):
        """Show file naming examples"""
        self.load_markdown_file("docs/FILE_NAMING_EXAMPLES.md")
    
    def show_troubleshooting(self):
        """Show troubleshooting information"""
        content = """🔍 Troubleshooting Common Issues

1. Authentication Issues:
   - Error: "credentials.json not found"
   - Solution: Run the API Setup Guide to create credentials
   
2. No Emails Found:
   - Check that Gmail labels are set up correctly: LinkedIn/Applied, LinkedIn/Viewed, LinkedIn/Rejected
   - Verify emails are labeled properly in Gmail
   
3. Parsing Errors:
   - Check that emails are from LinkedIn (not other job sites)
   - Verify email format hasn't changed
   
4. Permission Denied:
   - Ensure Gmail API is enabled in Google Cloud Console
   - Check OAuth consent screen is configured
   
5. GUI Not Responding:
   - Processing large amounts of emails takes time
   - Check console output for progress
   
6. Output File Issues:
   - Ensure you have write permissions to the output directory
   - Check that the file isn't open in another application

For more detailed troubleshooting, check the DOCUMENTATION.md file.
"""
        self.display_content(content)
    
    def load_markdown_file(self, file_path):
        """Load and display a markdown file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.display_markdown_content(content)
            else:
                self.display_content(f"Documentation file not found: {file_path}")
        except Exception as e:
            self.display_content(f"Error loading documentation: {e}")
    
    def display_markdown_content(self, content):
        """Display markdown content with basic formatting"""
        self.content_text.delete(1.0, tk.END)
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.content_text.insert(tk.END, line[2:] + '\n', 'heading1')
            elif line.startswith('## '):
                self.content_text.insert(tk.END, line[3:] + '\n', 'heading2')
            elif line.startswith('```'):
                continue  # Skip code block markers
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                self.content_text.insert(tk.END, '  • ' + line.strip()[2:] + '\n')
            elif '`' in line:
                # Handle inline code
                parts = line.split('`')
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        self.content_text.insert(tk.END, part)
                    else:
                        self.content_text.insert(tk.END, part, 'code')
                self.content_text.insert(tk.END, '\n')
            else:
                self.content_text.insert(tk.END, line + '\n')
    
    def display_content(self, content):
        """Display plain text content"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content)
    
    def open_readme(self):
        """Open README.md file"""
        readme_path = "README.md"
        if os.path.exists(readme_path):
            self.open_file(readme_path)
        else:
            messagebox.showerror("Error", "README.md not found")
    
    def open_docs_folder(self):
        """Open documentation folder"""
        docs_path = "docs"
        if os.path.exists(docs_path):
            self.open_folder(docs_path)
        else:
            messagebox.showerror("Error", "Documentation folder not found")
    
    def open_file(self, file_path):
        """Open a file with the default system application"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
    
    def open_folder(self, folder_path):
        """Open a folder with the default system file manager"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")


class APISetupWindow:
    """Dedicated window for API setup guidance"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Gmail API Setup Guide")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the API setup window UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Gmail API Setup Guide", 
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Step-by-step notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Step 1: Google Cloud Console
        step1_frame = ttk.Frame(notebook, padding="15")
        notebook.add(step1_frame, text="Step 1: Google Cloud Console")
        
        step1_content = """1. Create a Google Cloud Project

• Go to Google Cloud Console: https://console.cloud.google.com/
• Click "Select a project" → "New Project"
• Enter project name (e.g., "LinkedIn Job Tracker")
• Click "Create"

2. Enable Gmail API

• In the left sidebar, go to "APIs & Services" → "Library"
• Search for "Gmail API"
• Click on "Gmail API" and click "Enable"

3. Create Credentials

• Go to "APIs & Services" → "Credentials"
• Click "Create Credentials" → "OAuth client ID"
• If prompted, configure the OAuth consent screen first
• Choose "Desktop application" as application type
• Name it (e.g., "LinkedIn Job Tracker")
• Click "Create"

4. Download Credentials

• Click the download button (⬇) next to your OAuth client
• Save the file as "credentials.json" in your project root folder
"""
        
        step1_text = scrolledtext.ScrolledText(step1_frame, wrap=tk.WORD, height=20)
        step1_text.pack(fill=tk.BOTH, expand=True)
        step1_text.insert(1.0, step1_content)
        step1_text.config(state=tk.DISABLED)
        
        # Step 2: Gmail Labels
        step2_frame = ttk.Frame(notebook, padding="15")
        notebook.add(step2_frame, text="Step 2: Gmail Labels")
        
        step2_content = """Set up Gmail Labels for LinkedIn Notifications

1. Open Gmail in your web browser
2. In the left sidebar, scroll down to "Labels"
3. Click "Create new label"
4. Create the following label structure:

Required Labels:
• LinkedIn (parent label)
  • LinkedIn/Applied (child label)
  • LinkedIn/Viewed (child label)
  • LinkedIn/Rejected (child label)

How to create nested labels:
• For parent: Type "LinkedIn"
• For child: Type "LinkedIn/Applied" (the "/" creates nesting)

5. Apply labels to your LinkedIn emails:
• When you receive a LinkedIn job application confirmation, label it "LinkedIn/Applied"
• When you get a "viewed" notification, label it "LinkedIn/Viewed"
• When you get a rejection, label it "LinkedIn/Rejected"

Pro tip: Set up Gmail filters to automatically apply these labels based on email content!
"""
        
        step2_text = scrolledtext.ScrolledText(step2_frame, wrap=tk.WORD, height=20)
        step2_text.pack(fill=tk.BOTH, expand=True)
        step2_text.insert(1.0, step2_content)
        step2_text.config(state=tk.DISABLED)
        
        # Step 3: First Run
        step3_frame = ttk.Frame(notebook, padding="15")
        notebook.add(step3_frame, text="Step 3: First Run")
        
        step3_content = """First Time Setup

1. File Placement
• Ensure "credentials.json" is in your project root folder
• The file should be in the same directory as this GUI application

2. First Authentication
• Run the LinkedIn Job Tracker application
• Click "Start Processing"
• A web browser will open asking for permissions
• Sign in with your Google account
• Grant permissions to access Gmail
• The browser will show "The authentication flow has completed"

3. Token Storage
• After successful authentication, a "token.json" file will be created
• This file stores your authentication token for future use
• Keep this file secure and don't share it

4. Test the Setup
• Try running the application with a small date range first
• Check that it can find your labeled emails
• Verify the output CSV file is generated correctly

Troubleshooting:
• If you get "credentials.json not found" error, check file location
• If browser doesn't open, check your firewall settings
• If no emails found, verify your Gmail labels are set up correctly
"""
        
        step3_text = scrolledtext.ScrolledText(step3_frame, wrap=tk.WORD, height=20)
        step3_text.pack(fill=tk.BOTH, expand=True)
        step3_text.insert(1.0, step3_content)
        step3_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🌐 Open Google Cloud Console", 
                  command=lambda: webbrowser.open("https://console.cloud.google.com/")).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="📧 Open Gmail", 
                  command=lambda: webbrowser.open("https://mail.google.com/")).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="📖 View Credentials Setup", 
                  command=self.show_credentials_setup).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def show_credentials_setup(self):
        """Show the credentials setup documentation"""
        creds_path = "docs/CREDENTIALS_SETUP.md"
        if os.path.exists(creds_path):
            try:
                with open(creds_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a new window to display the content
                doc_window = tk.Toplevel(self.window)
                doc_window.title("Credentials Setup Documentation")
                doc_window.geometry("800x600")
                
                text_widget = scrolledtext.ScrolledText(doc_window, wrap=tk.WORD, 
                                                       font=("Consolas", 10))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load credentials setup: {e}")
        else:
            messagebox.showerror("Error", "Credentials setup documentation not found") 