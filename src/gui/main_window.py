"""
GUI Interface for LinkedIn Job Application Tracker

This module provides a user-friendly graphical interface for the EmailJobParser.
Users can select date ranges, view progress, and manage their job application tracking
without using command-line arguments.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
import subprocess
import platform
from datetime import datetime, timedelta
from tkinter import font
import re

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import authenticate
from parsers.linkedin.processor import process_gmail_labels_to_csv, LABELS
from utils.date_utils import get_date_range_query, get_date_range_description
from utils.archive_utils import perform_archive, get_archive_summary
from gui.help_window import HelpWindow, APISetupWindow

class EmailJobParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Job Application Tracker")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.selected_date_range = tk.StringVar(value="all")
        self.is_running = False
        self.current_progress = 0
        self.total_progress = 0
        self.output_file_path = None
        self.failure_log_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main user interface"""
        # Main container with fixed size
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Configure grid weights for dynamic layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Console area can expand
        
        # Set initial window size - RESIZABLE
        self.root.geometry("900x1000")
        self.root.minsize(700, 800)  # Minimum size to keep usable
        self.root.resizable(True, True)  # Enable resizing
        
        # Title
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        title_label = ttk.Label(main_frame, text="LinkedIn Job Application Tracker", font=title_font)
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W+tk.E)
        
        # Description
        desc_text = ("This tool processes your LinkedIn job application emails from Gmail.\n"
                    "Select a date range below to filter which emails to process.")
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.CENTER)
        desc_label.grid(row=1, column=0, pady=(0, 15), sticky=tk.W+tk.E)
        
        # Date Range Selection Frame - SCALABLE
        date_frame = ttk.LabelFrame(main_frame, text="Select Date Range", padding="10")
        date_frame.grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 15))
        date_frame.columnconfigure(0, weight=1)
        
        # Quick date range buttons
        self.create_date_buttons(date_frame)
        
        # Custom date range section
        self.create_custom_date_section(date_frame)
        
        # Selected range display
        self.selected_label = ttk.Label(date_frame, text="Selected: All time", 
                                       font=font.Font(weight="bold"))
        self.selected_label.grid(row=10, column=0, pady=(10, 0), sticky=tk.W+tk.E)
        
        # Action buttons - SCALABLE
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 15), sticky=tk.W+tk.E)
        button_frame.columnconfigure(0, weight=1)
        
        # Create two rows of buttons
        # Row 1: Main action buttons
        main_buttons = ttk.Frame(button_frame)
        main_buttons.grid(row=0, column=0, pady=(0, 8))
        
        self.run_button = ttk.Button(main_buttons, text="🚀 Start Processing", 
                                    command=self.start_processing, style="Accent.TButton")
        self.run_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.stop_button = ttk.Button(main_buttons, text="⏹ Stop", 
                                     command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.archive_button = ttk.Button(main_buttons, text="📦 Archive Files", 
                                       command=self.archive_files)
        self.archive_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # Row 2: Secondary buttons
        secondary_buttons = ttk.Frame(button_frame)
        secondary_buttons.grid(row=1, column=0)
        
        self.api_setup_button = ttk.Button(secondary_buttons, text="🔧 API Setup", 
                                         command=self.show_api_setup)
        self.api_setup_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.help_button = ttk.Button(secondary_buttons, text="❓ Help", 
                                    command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.open_folder_button = ttk.Button(secondary_buttons, text="📁 Open Output Folder", 
                                           command=self.open_output_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.open_file_button = ttk.Button(secondary_buttons, text="📄 Open Latest File", 
                                         command=self.open_latest_file, state=tk.DISABLED)
        self.open_file_button.pack(side=tk.LEFT)
        
        # Progress section - SCALABLE
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W+tk.E)
        
        # Email count display
        self.email_count_var = tk.StringVar(value="")
        self.email_count_label = ttk.Label(progress_frame, textvariable=self.email_count_var, 
                                          font=font.Font(size=10))
        self.email_count_label.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(3, 0))
        
        # Progress bar - SCALABLE
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(8, 0))
        
        # Progress percentage
        self.progress_percent_var = tk.StringVar(value="")
        self.progress_percent_label = ttk.Label(progress_frame, textvariable=self.progress_percent_var,
                                               font=font.Font(size=9))
        self.progress_percent_label.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(3, 0))
        
        # Console Output - SCALABLE (main expanding area)
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="10")
        console_frame.grid(row=5, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 15))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(1, weight=1)  # Console text area expands
        
        # Console controls
        console_controls = ttk.Frame(console_frame)
        console_controls.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 8))
        console_controls.columnconfigure(0, weight=1)
        
        ttk.Label(console_controls, text="Real-time processing output:", 
                 font=font.Font(size=9)).grid(row=0, column=0, sticky=tk.W)
        
        clear_button = ttk.Button(console_controls, text="Clear", 
                                 command=self.clear_log)
        clear_button.grid(row=0, column=1, sticky=tk.E)
        
        # Scalable console output - expands with window
        self.log_text = scrolledtext.ScrolledText(console_frame, 
                                                 height=10,    # Minimum height
                                                 width=50,     # Minimum width
                                                 bg='#f8f9fa', 
                                                 fg='#212529',
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Configure text tags for color coding
        self.log_text.tag_configure('success', foreground='#28a745')
        self.log_text.tag_configure('error', foreground='#dc3545')
        self.log_text.tag_configure('warning', foreground='#ffc107')
        self.log_text.tag_configure('info', foreground='#17a2b8')
        self.log_text.tag_configure('timestamp', foreground='#6c757d', font=('Consolas', 8))
        
        # Add initial welcome message
        self.log_message("🚀 LinkedIn Job Application Tracker ready!", 'info')
        self.log_message("Select a date range and click 'Start Processing' to begin.", 'info')
        
        # Status bar - SCALABLE
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, sticky=tk.W+tk.E, pady=(8, 0))
        
    def create_date_buttons(self, parent):
        """Create quick date range selection buttons"""
        quick_frame = ttk.Frame(parent)
        quick_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 15))
        
        # Configure columns to expand
        for i in range(3):
            quick_frame.columnconfigure(i, weight=1)
        
        # Date range options with descriptions
        date_options = [
            ("all", "All Time"),
            ("24h", "Last 24 Hours"),
            ("7d", "Last Week"),
            ("30d", "Last Month"),
            ("90d", "Last 3 Months"),
            ("1y", "Last Year")
        ]
        
        # Create buttons in a responsive grid
        for i, (value, text) in enumerate(date_options):
            row = i // 3
            col = i % 3
            
            btn = ttk.Radiobutton(quick_frame, text=text, variable=self.selected_date_range,
                                 value=value, command=self.update_selected_range)
            btn.grid(row=row, column=col, sticky=tk.W+tk.E, padx=5, pady=5)
            
    def create_custom_date_section(self, parent):
        """Create custom date range input section"""
        custom_frame = ttk.LabelFrame(parent, text="Custom Date Range", padding="10")
        custom_frame.grid(row=5, column=0, sticky=tk.W+tk.E, pady=(10, 0))
        custom_frame.columnconfigure(1, weight=1)
        custom_frame.columnconfigure(3, weight=1)
        
        # Custom date range radio button
        ttk.Radiobutton(custom_frame, text="Custom Range:", variable=self.selected_date_range,
                       value="custom", command=self.update_selected_range).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Start date
        ttk.Label(custom_frame, text="From:").grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        self.start_date_entry = ttk.Entry(custom_frame, width=12)
        self.start_date_entry.grid(row=0, column=2, sticky=tk.W+tk.E, padx=(0, 10))
        self.start_date_entry.insert(0, "2024-01-01")
        
        # End date
        ttk.Label(custom_frame, text="To:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.end_date_entry = ttk.Entry(custom_frame, width=12)
        self.end_date_entry.grid(row=0, column=4, sticky=tk.W+tk.E)
        self.end_date_entry.insert(0, "2024-12-31")
        
        # Format help
        help_text = "Format: YYYY-MM-DD (e.g., 2024-01-01)"
        ttk.Label(custom_frame, text=help_text, font=font.Font(size=8), 
                 foreground="gray").grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(5, 0))
    
    def update_selected_range(self):
        """Update the selected range display"""
        range_value = self.selected_date_range.get()
        
        if range_value == "custom":
            from_date = self.start_date_entry.get()
            to_date = self.end_date_entry.get()
            try:
                # Validate dates
                datetime.strptime(from_date, "%Y-%m-%d")
                datetime.strptime(to_date, "%Y-%m-%d")
                description = f"From {from_date} to {to_date}"
            except ValueError:
                description = "Custom range (invalid dates)"
        else:
            description = get_date_range_description(range_value)
        
        self.selected_label.config(text=f"Selected: {description}")
    
    def get_date_range_value(self):
        """Get the current date range value for processing"""
        if self.selected_date_range.get() == "custom":
            from_date = self.start_date_entry.get()
            to_date = self.end_date_entry.get()
            return f"{from_date}:{to_date}"
        else:
            return self.selected_date_range.get()
    
    def log_message(self, message, tag=''):
        """Add a message to the log display with optional tag for color coding"""
        if not message or not message.strip():
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Ensure we're on the main thread
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, lambda l=formatted_message.strip(): self._add_log_message(l, tag))
        else:
            self._add_log_message(formatted_message.strip(), tag)
    
    def _add_log_message(self, formatted_message, tag):
        """Internal method to add message to log (must be called from main thread)"""
        try:
            # Ensure the message ends with a newline for proper formatting
            if not formatted_message.endswith('\n'):
                formatted_message += '\n'
            
            # Insert the message
            self.log_text.insert(tk.END, formatted_message, tag)
            
            # Auto-scroll to bottom
            self.log_text.see(tk.END)
            
            # Limit log size to prevent memory issues (keep last 1000 lines)
            line_count = int(self.log_text.index('end-1c').split('.')[0])
            if line_count > 1000:
                self.log_text.delete('1.0', f'{line_count-1000}.0')
            
            # Force update for real-time display
            self.root.update_idletasks()
        except Exception as e:
            # Fallback in case of any GUI issues
            print(f"Log display error: {e}")
            
    def parse_and_log_message(self, message, skip_console=False):
        """Parse message for progress information and update GUI accordingly"""
        # Determine message type and color
        tag = ''
        if any(word in message.lower() for word in ['error', 'failed', 'exception']):
            tag = 'error'
        elif any(word in message.lower() for word in ['success', 'completed', 'done', 'finished']):
            tag = 'success'
        elif any(word in message.lower() for word in ['warning', 'warn']):
            tag = 'warning'
        elif any(word in message.lower() for word in ['processing', 'found', 'fetching', 'authenticating']):
            tag = 'info'
        
        # Log the message first with appropriate color (unless we're replacing)
        if not skip_console:
            self.log_message(message, tag)
        
        # Parse for progress information
        try:
            # Look for email count patterns
            if "Found approximately" in message and "messages in" in message:
                # Extract email count: "Found approximately 100 messages in LinkedIn/Applied"
                match = re.search(r'Found approximately (\d+) messages in (.+)', message)
                if match:
                    count = int(match.group(1))
                    label = match.group(2)
                    self.email_count_var.set(f"Found {count} emails in {label}")
                    
                    # Set up progress bar for this batch
                    if count > 0:
                        self.total_progress = count
                        self.current_progress = 0
                        self.progress_bar.config(mode='determinate', maximum=count, value=0)
                        self.progress_percent_var.set("0%")
            
            # Look for processing progress patterns
            elif "Processing Applied" in message or "Processing LinkedIn" in message:
                # Reset progress for new processing phase
                self.current_progress = 0
                self.progress_bar.config(value=0)
                self.progress_percent_var.set("0%")
            
            # Look for individual email processing (from tqdm or similar)
            elif "Applied" in message and "/" in message and "emails" in message:
                # Try to extract progress from messages like "Processing Applied email 50/100"
                match = re.search(r'(\d+)/(\d+)', message)
                if match:
                    current = int(match.group(1))
                    total = int(match.group(2))
                    self.current_progress = current
                    self.total_progress = total
                    self.progress_bar.config(maximum=total, value=current)
                    percent = int((current / total) * 100) if total > 0 else 0
                    self.progress_percent_var.set(f"{percent}%")
                    self.email_count_var.set(f"Processing {current}/{total} emails")
            
            # Look for completion messages
            elif "Successfully built database" in message:
                match = re.search(r'(\d+) unique applications', message)
                if match:
                    count = int(match.group(1))
                    self.email_count_var.set(f"✅ Found {count} unique applications")
                    self.progress_bar.config(value=self.progress_bar['maximum'])
                    self.progress_percent_var.set("100%")
            
            # Look for final file paths
            elif "📄 Main Report:" in message:
                # Extract file path for the "Open Latest File" button
                path_match = re.search(r'📄 Main Report: (.+)', message)
                if path_match:
                    self.output_file_path = path_match.group(1).strip()
                    self.open_file_button.config(state=tk.NORMAL)
            
            elif "📄 Error Log:" in message:
                # Extract failure log path
                path_match = re.search(r'📄 Error Log: (.+)', message)
                if path_match:
                    self.failure_log_path = path_match.group(1).strip()
                    
        except Exception as e:
            # If parsing fails, just log the original message
            pass
    
    def start_processing(self):
        """Start the email processing in a separate thread"""
        if self.is_running:
            return
        
        # Validate date range
        date_range = self.get_date_range_value()
        try:
            get_date_range_query(date_range)
        except ValueError as e:
            messagebox.showerror("Invalid Date Range", str(e))
            return
        
        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        
        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_emails, args=(date_range,))
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the processing (note: this is a request, actual stopping depends on the process)"""
        self.is_running = False
        self.log_message("⏹ Stop requested...", 'info')
        self.status_var.set("Stopping...")
    
    def open_output_folder(self):
        """Open the data/processed folder in the system file explorer"""
        try:
            output_dir = os.path.abspath("data/processed")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Cross-platform folder opening
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
                
            self.log_message(f"📁 Opened output folder: {output_dir}", 'info')
        except Exception as e:
            self.log_message(f"❌ Error opening folder: {e}", 'error')
            messagebox.showerror("Error", f"Could not open output folder:\n{e}")
    
    def open_latest_file(self):
        """Open the latest output file"""
        try:
            if self.output_file_path and os.path.exists(self.output_file_path):
                # Cross-platform file opening
                if platform.system() == "Windows":
                    os.startfile(self.output_file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", self.output_file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", self.output_file_path])
                    
                self.log_message(f"📄 Opened file: {os.path.basename(self.output_file_path)}", 'info')
            else:
                self.log_message("No output file available to open. Run processing first.", 'warning')
                messagebox.showwarning("No File", "No output file available to open.\nRun processing first.")
        except Exception as e:
            self.log_message(f"❌ Error opening file: {e}", 'error')
            messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def archive_files(self):
        """Archive processed files to organized folders"""
        try:
            self.log_message("📦 Starting archive operation...", 'info')
            self.status_var.set("Archiving files...")
            
            # Force GUI update to show the status
            self.root.update_idletasks()
            
            # Perform the archive operation
            success, results = perform_archive()
            
            if success:
                summary = get_archive_summary(results)
                self.log_message("📦 Archive completed successfully!", 'success')
                
                # Log detailed results
                for line in summary.split('\n'):
                    if line.strip():
                        if line.startswith('📦') or line.startswith('📊'):
                            self.log_message(line, 'success')
                        elif line.startswith('⚠️'):
                            self.log_message(line, 'warning')
                        else:
                            self.log_message(line, 'info')
                
                self.status_var.set("Archive completed")
                
                # Check if there were any errors during archiving
                if 'errors' in results and results['errors']:
                    warning_msg = (f"Archive completed with {len(results['errors'])} warnings.\n\n"
                                 f"Total files archived: {results['total_archived']}\n"
                                 f"Archive location: {results['archive_dirs']['base']}\n\n"
                                 f"Check the console output for detailed information about warnings.")
                    messagebox.showwarning("Archive Completed with Warnings", warning_msg)
                else:
                    # Show success dialog
                    messagebox.showinfo("Archive Complete", 
                        f"Files archived successfully!\n\n"
                        f"Total files archived: {results['total_archived']}\n"
                        f"Archive location: {results['archive_dirs']['base']}\n\n"
                        f"Check the console output for detailed information.")
                
            else:
                error_msg = results.get('message', 'Unknown error occurred')
                error_type = results.get('error_type', 'unknown')
                
                self.log_message(f"❌ Archive failed: {error_msg}", 'error')
                self.status_var.set("Archive failed")
                
                # Provide specific error messages based on error type
                if error_type == 'permission_error':
                    dialog_msg = (f"Archive failed due to permission issues:\n\n{error_msg}\n\n"
                                f"Try running as administrator or check folder permissions.")
                elif error_type == 'os_error':
                    dialog_msg = (f"Archive failed due to system error:\n\n{error_msg}\n\n"
                                f"Check available disk space and file system permissions.")
                elif error_type == 'no_files':
                    dialog_msg = (f"No files found to archive.\n\n"
                                f"Process some emails first to generate files for archiving.")
                elif error_type == 'archiving_error':
                    dialog_msg = (f"Error during file archiving:\n\n{error_msg}\n\n"
                                f"Some files may be in use or have permission issues.")
                else:
                    dialog_msg = f"Archive operation failed:\n\n{error_msg}"
                
                messagebox.showerror("Archive Failed", dialog_msg)
                
        except KeyboardInterrupt:
            self.log_message("⏹ Archive operation cancelled by user", 'warning')
            self.status_var.set("Archive cancelled")
            messagebox.showinfo("Archive Cancelled", "Archive operation was cancelled by user.")
        except Exception as e:
            self.log_message(f"❌ Archive error: {str(e)}", 'error')
            self.status_var.set("Archive error")
            messagebox.showerror("Archive Error", 
                f"An unexpected error occurred during archiving:\n\n{str(e)}\n\n"
                f"Check the console output for more details.")
    
    def process_emails(self, date_range):
        """Process emails with the selected date range"""
        try:
            self.progress_var.set("Authenticating with Gmail...")
            self.status_var.set("Authenticating...")
            self.log_message("🔐 Authenticating with Gmail...", 'info')
            
            service = authenticate()
            if not service:
                raise Exception("Authentication failed")
            
            self.log_message("✅ Authentication successful", 'success')
            
            if not self.is_running:
                return
            
            self.progress_var.set("Fetching Gmail labels...")
            self.status_var.set("Fetching labels...")
            self.log_message("📋 Fetching Gmail labels...", 'info')
            
            all_labels = service.users().labels().list(userId='me').execute().get('labels', [])
            
            if not self.is_running:
                return
            
            self.progress_var.set("Processing emails...")
            self.status_var.set("Processing...")
            self.log_message(f"📧 Processing emails for date range: {get_date_range_description(date_range)}", 'info')
            
            # Redirect stdout to capture print statements and parse progress
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            class GUILogger:
                def __init__(self, gui):
                    self.gui = gui
                    self.buffer = ""
                    self.last_progress_line = None
                    self.progress_patterns = [
                        r'Processing Applied.*?(\d+)/(\d+)',
                        r'Processing LinkedIn.*?(\d+)/(\d+)', 
                        r'Processing.*?(\d+%)',
                        r'Fetching page \d+',
                        r'Retrieved \d+ messages so far',
                        r'Found \d+ .* emails to process',
                        r'\d+%\|[█▉▊▋▌▍▎▏#\s]*\|',  # tqdm progress bar pattern
                        r'Processing.*?:\s*\d+%\|',  # tqdm with description and bar
                        r'^\s*\d+/\d+\s*\[\d+:\d+<\d+:\d+',  # tqdm format with time
                        r'^\s*\d+it\s*\[\d+:\d+',  # tqdm iterations
                        r'Processing.*?Messages:\s*\d+%',
                        r'^\s*\d+%\|',  # Simple tqdm percentage with bar
                        r'Processing Applied:\s*\d+%\|',  # tqdm with Applied description
                        r'Processing LinkedIn/\w+:\s*\d+%\|',  # tqdm with LinkedIn labels
                        r'^\s*\d+/\d+\s*\[\d+:\d+<\d+:\d+,\s*[\d.]+it/s\]',  # Full tqdm pattern
                        r'^\s*\d+%\|[█▉▊▋▌▍▎▏#\s]*\|\s*\d+/\d+\s*\[',  # Complete tqdm bar
                        r'^\s*\d+it\s*\[\d+:\d+,\s*[\d.]+it/s\]'  # tqdm iterations with rate
                    ]
                    
                def is_progress_update(self, text):
                    """Check if text is a progress update that should replace the previous line"""
                    import re
                    for pattern in self.progress_patterns:
                        if re.search(pattern, text):
                            return True
                    return False
                    
                def write(self, text):
                    if text:
                        # Handle both single characters and full lines
                        self.buffer += text
                        
                        # Handle carriage return updates (like tqdm) first
                        if '\r' in self.buffer:
                            parts = self.buffer.split('\r')
                            # Process only the last non-empty part as progress update
                            for part in parts[:-1]:
                                if part.strip():
                                    self._process_line(part.strip(), is_progress_update=True)
                            # Keep the last part in buffer
                            self.buffer = parts[-1]
                        
                        # Process complete lines (newline-terminated)
                        while '\n' in self.buffer:
                            line, self.buffer = self.buffer.split('\n', 1)
                            if line.strip():
                                self._process_line(line.strip())
                    
                    # Force GUI update for real-time display
                    self.gui.root.update_idletasks()
                    
                def _process_line(self, line, is_progress_update=False):
                    """Process a single line of output"""
                    # Skip empty lines
                    if not line.strip():
                        return
                    
                    # Check if this is a progress update
                    if is_progress_update or self.is_progress_update(line):
                        # For tqdm progress updates, suppress intermediate updates
                        # Only show the final 100% completion, and avoid duplicates
                        if "100%" in line and ("|" in line or "it/s]" in line):
                            # Check if this is a duplicate of the last progress line
                            if self.last_progress_line and self.last_progress_line.strip() == line.strip():
                                return  # Skip duplicate
                            # This is a completion message - show it
                            self.gui.root.after(0, lambda l=line: self.gui.parse_and_log_message(l))
                        # For all other progress updates, just update the progress bar silently
                        else:
                            self.gui.root.after(0, lambda l=line: self.gui.parse_and_log_message(l, skip_console=True))
                        self.last_progress_line = line
                    else:
                        # Regular message - reset progress tracking
                        self.last_progress_line = None
                        self.gui.root.after(0, lambda l=line: self.gui.parse_and_log_message(l))
                

                    
                def flush(self):
                    # Process any remaining buffer content, but avoid duplicate progress bars
                    if self.buffer.strip():
                        line = self.buffer.strip()
                        # Skip empty lines and duplicate progress completions
                        if line and not (self.last_progress_line and self.last_progress_line.strip() == line.strip()):
                            self._process_line(line)
                        self.buffer = ""
                    self.gui.root.update_idletasks()
            
            # Redirect both stdout and stderr to GUI
            gui_logger = GUILogger(self)
            sys.stdout = gui_logger
            sys.stderr = gui_logger
            
            try:
                success = process_gmail_labels_to_csv(service, LABELS, all_labels, date_range)
                
                if success:
                    self.log_message("🎉 Processing completed successfully!", 'success')
                    self.progress_var.set("Completed successfully!")
                    self.status_var.set("Completed")
                    self.progress_bar.config(value=self.progress_bar['maximum'])
                    self.progress_percent_var.set("100%")
                    
                    # Show success message with date range info
                    date_desc = get_date_range_description(date_range)
                    file_info = ""
                    if self.output_file_path:
                        file_info = f"\n\nOutput file: {os.path.basename(self.output_file_path)}"
                    
                    messagebox.showinfo("Success", 
                        f"Email processing completed successfully!\n\n"
                        f"Date range: {date_desc}{file_info}\n"
                        f"Use the 'Open Output Folder' button to view files.")
                else:
                    self.log_message("❌ Processing failed", 'error')
                    self.progress_var.set("Processing failed")
                    self.status_var.set("Failed")
                    self.progress_bar.config(mode='indeterminate')
                    self.progress_percent_var.set("")
                    messagebox.showerror("Error", "Processing failed. Check the log for details.")
                    
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}", 'error')
            self.progress_var.set("Error occurred")
            self.status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
        finally:
            self.is_running = False
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar.stop()
            
            # Reset progress indicators if not completed successfully
            if not success:
                self.email_count_var.set("")
                self.progress_percent_var.set("")

    def show_api_setup(self):
        """Show the API setup guide window"""
        try:
            APISetupWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open API setup guide: {e}")
    
    def show_help(self):
        """Show the main help window"""
        try:
            HelpWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open help window: {e}")

    def clear_log(self):
        """Clear the console output log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Console cleared.", 'info')

def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = EmailJobParserGUI(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 