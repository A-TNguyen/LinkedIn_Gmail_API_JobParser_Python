"""
Date Range Utilities for Gmail Search

This module provides utilities for handling date ranges in Gmail API searches.
It supports common date range presets and custom date ranges.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re

def get_date_range_query(date_range: str) -> str:
    """
    Convert a date range string to Gmail search query format.
    
    Args:
        date_range: One of 'all', '24h', '1d', '7d', '1w', '30d', '1m', '90d', '3m', '1y'
                   or a custom range like '2024-01-01:2024-12-31'
    
    Returns:
        Gmail search query string for date filtering
    """
    if not date_range or date_range.lower() == 'all':
        return ''
    
    # Handle custom date ranges (YYYY-MM-DD:YYYY-MM-DD)
    if ':' in date_range:
        return _parse_custom_date_range(date_range)
    
    # Handle preset date ranges
    date_range = date_range.lower()
    now = datetime.now()
    
    if date_range in ['24h', '1d']:
        # Last 24 hours
        start_date = now - timedelta(days=1)
        return f"after:{start_date.strftime('%Y/%m/%d')}"
    
    elif date_range in ['7d', '1w']:
        # Last 7 days
        start_date = now - timedelta(days=7)
        return f"after:{start_date.strftime('%Y/%m/%d')}"
    
    elif date_range in ['30d', '1m']:
        # Last 30 days
        start_date = now - timedelta(days=30)
        return f"after:{start_date.strftime('%Y/%m/%d')}"
    
    elif date_range in ['90d', '3m']:
        # Last 90 days
        start_date = now - timedelta(days=90)
        return f"after:{start_date.strftime('%Y/%m/%d')}"
    
    elif date_range == '1y':
        # Last year
        start_date = now - timedelta(days=365)
        return f"after:{start_date.strftime('%Y/%m/%d')}"
    
    else:
        raise ValueError(f"Unknown date range: {date_range}")

def _parse_custom_date_range(date_range: str) -> str:
    """
    Parse custom date range in format YYYY-MM-DD:YYYY-MM-DD.
    
    Args:
        date_range: Custom date range string
    
    Returns:
        Gmail search query string
    """
    try:
        start_str, end_str = date_range.split(':')
        
        # Validate date format
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
        
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        
        # Convert to Gmail search format
        start_gmail = start_date.strftime('%Y/%m/%d')
        end_gmail = end_date.strftime('%Y/%m/%d')
        
        return f"after:{start_gmail} before:{end_gmail}"
    
    except ValueError as e:
        if "time data" in str(e):
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD:YYYY-MM-DD format")
        raise

def get_date_range_description(date_range: str) -> str:
    """
    Get a human-readable description of the date range.
    
    Args:
        date_range: Date range string
    
    Returns:
        Human-readable description
    """
    if not date_range or date_range.lower() == 'all':
        return 'All time'
    
    if ':' in date_range:
        start_str, end_str = date_range.split(':')
        return f'From {start_str} to {end_str}'
    
    date_range = date_range.lower()
    descriptions = {
        '24h': 'Last 24 hours',
        '1d': 'Last 24 hours',
        '7d': 'Last 7 days',
        '1w': 'Last week',
        '30d': 'Last 30 days',
        '1m': 'Last month',
        '90d': 'Last 90 days',
        '3m': 'Last 3 months',
        '1y': 'Last year'
    }
    
    return descriptions.get(date_range, f'Unknown range: {date_range}')

def validate_date_range(date_range: str) -> bool:
    """
    Validate if a date range string is valid.
    
    Args:
        date_range: Date range string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        get_date_range_query(date_range)
        return True
    except ValueError:
        return False

def get_available_date_ranges() -> dict:
    """
    Get all available preset date ranges.
    
    Returns:
        Dictionary of date range codes and descriptions
    """
    return {
        'all': 'All time',
        '24h': 'Last 24 hours',
        '1d': 'Last 24 hours',
        '7d': 'Last 7 days',
        '1w': 'Last week',
        '30d': 'Last 30 days',
        '1m': 'Last month',
        '90d': 'Last 90 days',
        '3m': 'Last 3 months',
        '1y': 'Last year',
        'custom': 'Custom range (YYYY-MM-DD:YYYY-MM-DD)'
    } 