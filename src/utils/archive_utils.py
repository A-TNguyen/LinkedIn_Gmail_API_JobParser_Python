#!/usr/bin/env python3
"""
Archive Utilities for LinkedIn Job Application Tracker

This module provides functionality to archive processed files into organized folders.
"""

import os
import shutil
import glob
from datetime import datetime
from typing import List, Tuple

def get_unique_filename(destination_path: str) -> str:
    """
    Generate a unique filename if the destination already exists.
    Adds (1), (2), etc. suffix before the file extension.
    
    Args:
        destination_path: The original destination path
        
    Returns:
        A unique destination path
    """
    if not os.path.exists(destination_path):
        return destination_path
    
    # Split the path into directory, name, and extension
    dir_path = os.path.dirname(destination_path)
    filename = os.path.basename(destination_path)
    
    # Split filename into name and extension
    if '.' in filename:
        name, ext = os.path.splitext(filename)
    else:
        name, ext = filename, ''
    
    # Find the next available number
    counter = 1
    while True:
        new_filename = f"{name} ({counter}){ext}"
        new_path = os.path.join(dir_path, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def create_archive_structure(base_archive_dir: str = "data/archive") -> dict:
    """
    Create the archive folder structure.
    
    Args:
        base_archive_dir: Base directory for archives
        
    Returns:
        Dictionary with archive directory paths
        
    Raises:
        OSError: If directory creation fails
        PermissionError: If insufficient permissions
    """
    archive_dirs = {
        'base': base_archive_dir,
        'job_applications': os.path.join(base_archive_dir, 'job_applications'),
        'failed_verifications': os.path.join(base_archive_dir, 'failed_verifications'),
        'logs': os.path.join(base_archive_dir, 'logs')
    }
    
    # Create directories if they don't exist
    for dir_name, dir_path in archive_dirs.items():
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created/verified directory: {dir_path}")
        except PermissionError as e:
            raise PermissionError(f"Permission denied creating {dir_name} directory '{dir_path}': {e}")
        except OSError as e:
            raise OSError(f"Failed to create {dir_name} directory '{dir_path}': {e}")
        except Exception as e:
            raise Exception(f"Unexpected error creating {dir_name} directory '{dir_path}': {e}")
    
    return archive_dirs

def get_files_to_archive(processed_dir: str = "data/processed") -> dict:
    """
    Get lists of files that can be archived.
    
    Args:
        processed_dir: Directory containing processed files
        
    Returns:
        Dictionary with categorized file lists
        
    Raises:
        OSError: If directory access fails
    """
    files = {
        'job_applications': [],
        'failed_verifications': [],
        'logs': []
    }
    
    # Only check the processed directory for files to archive
    directories_to_check = [processed_dir]
    
    try:
        for check_dir in directories_to_check:
            if not os.path.exists(check_dir):
                print(f"⚠️ Directory does not exist: {check_dir}")
                continue
            
            print(f"🔍 Checking directory: {check_dir}")
            
            # Find job application status files
            try:
                job_app_pattern = os.path.join(check_dir, "job_application_status_*.csv")
                dir_job_files = glob.glob(job_app_pattern)
                files['job_applications'].extend(dir_job_files)
                if dir_job_files:
                    print(f"📋 Found {len(dir_job_files)} job application files in {check_dir}")
            except Exception as e:
                print(f"⚠️ Error searching for job application files in {check_dir}: {e}")
            
            # Find failed verification files
            try:
                failed_pattern = os.path.join(check_dir, "failed_verifications_*.csv")
                dir_failed_files = glob.glob(failed_pattern)
                files['failed_verifications'].extend(dir_failed_files)
                if dir_failed_files:
                    print(f"❌ Found {len(dir_failed_files)} failed verification files in {check_dir}")
            except Exception as e:
                print(f"⚠️ Error searching for failed verification files in {check_dir}: {e}")
            
            # Find log files (only check data/logs directory for the processed_dir)
            if check_dir == processed_dir:
                try:
                    logs_dir = "data/logs"
                    if os.path.exists(logs_dir):
                        log_pattern = os.path.join(logs_dir, "*.log")
                        dir_log_files = glob.glob(log_pattern)
                        files['logs'].extend(dir_log_files)
                        if dir_log_files:
                            print(f"📝 Found {len(dir_log_files)} log files in {logs_dir}")
                    else:
                        print(f"⚠️ Logs directory does not exist: {logs_dir}")
                except Exception as e:
                    print(f"⚠️ Error searching for log files: {e}")
        
        # Print summary
        print(f"📊 Total files found: {len(files['job_applications'])} job applications, {len(files['failed_verifications'])} failed verifications, {len(files['logs'])} logs")
        
    except OSError as e:
        raise OSError(f"Failed to access processed directory '{processed_dir}': {e}")
    except Exception as e:
        raise Exception(f"Unexpected error while searching for files: {e}")
    
    return files

def archive_files(files_to_archive: dict, archive_dirs: dict) -> dict:
    """
    Archive files to their respective directories.
    
    Args:
        files_to_archive: Dictionary with categorized file lists
        archive_dirs: Dictionary with archive directory paths
        
    Returns:
        Dictionary with archive results
    """
    results = {
        'job_applications': {'count': 0, 'files': []},
        'failed_verifications': {'count': 0, 'files': []},
        'logs': {'count': 0, 'files': []},
        'errors': []
    }
    
    # Archive job application files
    print(f"📋 Archiving {len(files_to_archive['job_applications'])} job application files...")
    for file_path in files_to_archive['job_applications']:
        try:
            if not os.path.exists(file_path):
                results['errors'].append(f"Source file not found: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            destination = os.path.join(archive_dirs['job_applications'], filename)
            
            # Get unique filename if destination already exists
            unique_destination = get_unique_filename(destination)
            unique_filename = os.path.basename(unique_destination)
            
            # Perform the move operation
            shutil.move(file_path, unique_destination)
            results['job_applications']['files'].append(unique_filename)
            results['job_applications']['count'] += 1
            print(f"✅ Archived and deleted original: {unique_filename}")
            
        except PermissionError as e:
            error_msg = f"Permission denied moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except shutil.Error as e:
            error_msg = f"File operation error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except OSError as e:
            error_msg = f"OS error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    # Archive failed verification files
    print(f"❌ Archiving {len(files_to_archive['failed_verifications'])} failed verification files...")
    for file_path in files_to_archive['failed_verifications']:
        try:
            if not os.path.exists(file_path):
                results['errors'].append(f"Source file not found: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            destination = os.path.join(archive_dirs['failed_verifications'], filename)
            
            # Get unique filename if destination already exists
            unique_destination = get_unique_filename(destination)
            unique_filename = os.path.basename(unique_destination)
            
            # Perform the move operation
            shutil.move(file_path, unique_destination)
            results['failed_verifications']['files'].append(unique_filename)
            results['failed_verifications']['count'] += 1
            print(f"✅ Archived and deleted original: {unique_filename}")
            
        except PermissionError as e:
            error_msg = f"Permission denied moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except shutil.Error as e:
            error_msg = f"File operation error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except OSError as e:
            error_msg = f"OS error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error moving {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    # Archive log files (copy, don't move, to keep current logs accessible)
    print(f"📝 Archiving {len(files_to_archive['logs'])} log files...")
    for file_path in files_to_archive['logs']:
        try:
            if not os.path.exists(file_path):
                results['errors'].append(f"Source file not found: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_filename = f"{timestamp}_{filename}"
            destination = os.path.join(archive_dirs['logs'], archived_filename)
            
            # Get unique filename if destination already exists (unlikely with timestamp, but safe)
            unique_destination = get_unique_filename(destination)
            unique_filename = os.path.basename(unique_destination)
            
            # Perform the copy operation
            shutil.copy2(file_path, unique_destination)
            results['logs']['files'].append(unique_filename)
            results['logs']['count'] += 1
            print(f"✅ Archived: {unique_filename}")
            
        except PermissionError as e:
            error_msg = f"Permission denied copying {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except shutil.Error as e:
            error_msg = f"File operation error copying {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except OSError as e:
            error_msg = f"OS error copying {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error copying {file_path}: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    return results

def perform_archive() -> Tuple[bool, dict]:
    """
    Perform complete archive operation.
    
    Returns:
        Tuple of (success, results_dict)
    """
    print("🗂️ Starting archive operation...")
    
    try:
        # Create archive structure
        print("📁 Creating archive directory structure...")
        try:
            archive_dirs = create_archive_structure()
            print("✅ Archive directory structure created successfully")
        except PermissionError as e:
            error_msg = f"Permission denied creating archive directories: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'permission_error'}
        except OSError as e:
            error_msg = f"OS error creating archive directories: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'os_error'}
        except Exception as e:
            error_msg = f"Unexpected error creating archive directories: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'unexpected_error'}
        
        # Get files to archive
        print("🔍 Searching for files to archive...")
        try:
            files_to_archive = get_files_to_archive()
            print("✅ File search completed")
        except OSError as e:
            error_msg = f"OS error searching for files: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'os_error'}
        except Exception as e:
            error_msg = f"Unexpected error searching for files: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'unexpected_error'}
        
        # Check if there are any files to archive
        total_files = (len(files_to_archive['job_applications']) + 
                      len(files_to_archive['failed_verifications']) + 
                      len(files_to_archive['logs']))
        
        if total_files == 0:
            message = 'No files found to archive'
            print(f"⚠️ {message}")
            return False, {'message': message, 'error_type': 'no_files'}
        
        print(f"📊 Found {total_files} total files to archive")
        
        # Archive the files
        print("🗂️ Starting file archiving process...")
        try:
            results = archive_files(files_to_archive, archive_dirs)
            print("✅ File archiving process completed")
        except Exception as e:
            error_msg = f"Error during file archiving: {e}"
            print(f"❌ {error_msg}")
            return False, {'message': error_msg, 'error_type': 'archiving_error'}
        
        # Add summary information
        results['archive_dirs'] = archive_dirs
        results['total_archived'] = (results['job_applications']['count'] + 
                                   results['failed_verifications']['count'] + 
                                   results['logs']['count'])
        
        # Determine success based on whether any files were archived and error count
        files_archived = results['total_archived'] > 0
        has_errors = len(results['errors']) > 0
        
        if files_archived and not has_errors:
            print(f"🎉 Archive operation completed successfully! {results['total_archived']} files archived.")
            success = True
        elif files_archived and has_errors:
            print(f"⚠️ Archive operation completed with warnings. {results['total_archived']} files archived, {len(results['errors'])} errors.")
            success = True  # Partial success - some files were archived
        else:
            print(f"❌ Archive operation failed. No files were archived. {len(results['errors'])} errors.")
            success = False
        
        return success, results
        
    except KeyboardInterrupt:
        error_msg = "Archive operation cancelled by user"
        print(f"⏹ {error_msg}")
        return False, {'message': error_msg, 'error_type': 'user_cancelled'}
    except Exception as e:
        error_msg = f'Archive operation failed with unexpected error: {e}'
        print(f"❌ {error_msg}")
        return False, {'message': error_msg, 'error_type': 'unexpected_error'}

def get_archive_summary(results: dict) -> str:
    """
    Generate a human-readable summary of archive results.
    
    Args:
        results: Results dictionary from archive operation
        
    Returns:
        Formatted summary string
    """
    if 'message' in results:
        return results['message']
    
    summary_lines = []
    summary_lines.append(f"📦 Archive completed successfully!")
    summary_lines.append(f"📊 Total files archived: {results['total_archived']}")
    summary_lines.append("")
    
    if results['job_applications']['count'] > 0:
        summary_lines.append(f"📋 Job Applications: {results['job_applications']['count']} files")
        for filename in results['job_applications']['files']:
            summary_lines.append(f"   • {filename}")
        summary_lines.append("")
    
    if results['failed_verifications']['count'] > 0:
        summary_lines.append(f"❌ Failed Verifications: {results['failed_verifications']['count']} files")
        for filename in results['failed_verifications']['files']:
            summary_lines.append(f"   • {filename}")
        summary_lines.append("")
    
    if results['logs']['count'] > 0:
        summary_lines.append(f"📝 Logs: {results['logs']['count']} files")
        for filename in results['logs']['files']:
            summary_lines.append(f"   • {filename}")
        summary_lines.append("")
    
    summary_lines.append(f"📁 Archive location: {results['archive_dirs']['base']}")
    
    if results['errors']:
        summary_lines.append("")
        summary_lines.append("⚠️ Errors encountered:")
        for error in results['errors']:
            summary_lines.append(f"   • {error}")
    
    return "\n".join(summary_lines) 