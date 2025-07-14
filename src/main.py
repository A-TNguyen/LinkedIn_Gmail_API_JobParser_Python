import sys
import os

# Add the 'src' directory to the Python path to ensure robust imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.auth import authenticate
from parser_runner import run_enabled_parsers
from utils.logging_utils import setup_logging, restore_logging

def main():
    """
    The main entry point for the Gmail Job Application Parser.

    This function orchestrates the entire process:
    1. Sets up logging to capture all console output.
    2. Authenticates with the Gmail API.
    3. Calls the master parser runner, which executes all enabled parser modules.
    4. Restores logging and exits.
    """
    original_stdout, log_file = None, None
    try:
        # --- Logging Setup ---
        # All print statements will now be written to both console and log file
        original_stdout, log_file = setup_logging()
        
        # --- Authentication ---
        print("\n--- Step 1: Authenticating with Gmail ---")
        service = authenticate()
        if not service:
            print("❌ Authentication failed. Exiting.")
            sys.exit(1)
        print("✅ Authentication successful.")

        # --- Processing ---
        print("\n--- Step 2: Handing off to the master parser runner ---")
        success = run_enabled_parsers(service)
        
        if not success:
            print("\n--- SCRIPT HALTED due to a critical error in one of the parsers. ---")
            sys.exit(1)

    except Exception as e:
        print(f"\n\n====================== UNHANDLED EXCEPTION ======================")
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print(f"===================================================================")
        
    finally:
        # --- Cleanup ---
        # Restore original stdout and close the log file
        print("\n--- All parser runs finished. ---")
        restore_logging(original_stdout, log_file)
        
if __name__ == '__main__':
    main() 