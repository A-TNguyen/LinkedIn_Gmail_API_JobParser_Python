import os
import sys
import argparse
from datetime import datetime

# Add the 'src' directory to the Python path to ensure robust imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from utils.auth import authenticate
from parsers.linkedin.processor import process_gmail_labels_to_csv, LABELS
from utils.date_utils import get_available_date_ranges, validate_date_range

def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Tracker')
    parser.add_argument('--date-range', '-d', 
                       default='all',
                       help='Date range to process (all, 24h, 7d, 30d, 90d, 1y, or YYYY-MM-DD:YYYY-MM-DD)')
    parser.add_argument('--list-ranges', '-l', 
                       action='store_true',
                       help='List available date ranges and exit')
    
    args = parser.parse_args()
    
    # Handle list ranges option
    if args.list_ranges:
        print("Available date ranges:")
        for code, description in get_available_date_ranges().items():
            print(f"  {code:8} - {description}")
        return
    
    # Validate date range
    if not validate_date_range(args.date_range):
        print(f"❌ Invalid date range: {args.date_range}")
        print("Use --list-ranges to see available options")
        return
    
    # Set up logging to a file
    log_file_path = "data/logs/parser_run.log"
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    original_stdout = sys.stdout
    success = False
    try:
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            # Redirect stdout to both console and log file
            class Tee(object):
                def __init__(self, *files):
                    self.files = files
                def write(self, obj):
                    for f in self.files:
                        f.write(obj)
                        f.flush()
                def flush(self):
                    for f in self.files:
                        f.flush()

            sys.stdout = Tee(sys.stdout, log_file)
            
            print(f"\n\n--- Parser started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            service = authenticate()
            if not service:
                print("Authentication failed. Exiting.")
                return

            try:
                # Get all available labels from Gmail
                all_labels = service.users().labels().list(userId='me').execute().get('labels', [])
                
                # Run the main parser
                success = process_gmail_labels_to_csv(service, LABELS, all_labels, args.date_range)

            except Exception as e:
                print(f'An unexpected error occurred in main: {e}')
                success = False

    finally:
        sys.stdout = original_stdout
        if not success:
            print("\n❌ The script encountered a critical error. Check the logs for details.")
            sys.exit(1)

if __name__ == '__main__':
    main() 