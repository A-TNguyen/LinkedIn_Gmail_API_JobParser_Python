import sys
import os
from datetime import datetime

def setup_logging(log_file_path="logs/parser_run.log"):
    """
    Sets up logging to redirect stdout to both the console and a log file.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        A reference to the original stdout, which can be used to restore it later.
    """
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    original_stdout = sys.stdout
    log_file = open(log_file_path, 'a', encoding='utf-8')

    class Tee(object):
        """A helper class to redirect stdout to multiple file-like objects."""
        def __init__(self, *files):
            """Initializes the Tee object with one or more file targets."""
            self.files = files
        def write(self, obj):
            """Writes the given object to all registered files."""
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            """Flushes all registered files."""
            for f in self.files:
                f.flush()

    sys.stdout = Tee(original_stdout, log_file)
    print(f"\n\n--- Parser started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    return original_stdout, log_file

def restore_logging(original_stdout, log_file):
    """
    Restores the original stdout and closes the log file.

    Args:
        original_stdout: The original sys.stdout object to restore.
        log_file: The log file object to close.
    """
    sys.stdout = original_stdout
    if log_file:
        log_file.close() 