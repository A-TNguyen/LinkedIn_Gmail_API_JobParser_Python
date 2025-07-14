import os
import csv
from datetime import datetime

def write_data_to_csv(data: list, filename: str):
    """
    Writes a list of dictionaries to a CSV file.

    The columns are fixed to ensure consistent output.

    Args:
        data: A list of dictionaries, where each dictionary represents a row.
        filename: The path to the output CSV file.
    """
    fieldnames = ["Company Name", "Job Title", "Status", "Date", "Location", "Metadata Subject", "Comment"]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"❌ An error occurred while writing to '{filename}': {e}")

def write_failures_to_csv(failures: list, filename: str):
    """
    Appends a list of failure records to the designated failure log CSV file.

    If the file doesn't exist, it creates it and writes the header row.

    Args:
        failures: A list of dictionaries, where each dictionary is a failure record.
        filename: The path to the failure log file.
    """
    file_exists = os.path.isfile(filename)
    fieldnames = ['Timestamp', 'Email ID', 'Label', 'Reason', 'Date', 'Company Name', 'Job Title', 'Location', 'Status', 'Metadata', 'Comment']
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(failures)
    except Exception as e:
        print(f"Error writing failures to CSV: {e}")

def archive_report(output_file: str, archive_dir: str) -> str:
    """
    Archives the previous report file by moving it to the archive directory with a timestamp.

    Args:
        output_file: The path to the file to be archived.
        archive_dir: The directory where the file should be archived.

    Returns:
        The full path to the newly archived file, or None if no file was archived.
    """
    if os.path.exists(output_file):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file_name = f"job_application_status_{timestamp}.csv"
            archive_path = os.path.join(archive_dir, archive_file_name)
            os.rename(output_file, archive_path)
            print(f"🗄️ Previous output file archived.")
            return os.path.abspath(archive_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not archive old output file. It will be overwritten. Error: {e}")
    return None 