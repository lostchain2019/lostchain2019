"""
Datetime utility functions for parsing and formatting.
"""
import pandas as pd
import numpy as np
import re
from config.constants import DATETIME_FORMATS
from config.dependencies import DATEUTIL_AVAILABLE, dateutil_parse


def fix_datetime_string(dt_str):
    """Fix datetime string by adding seconds if missing"""
    if pd.isna(dt_str) or not str(dt_str).strip():
        return dt_str
    
    dt_str = str(dt_str).strip()
    
    # Check if the time part has seconds (HH:MM:SS format)
    # Split by space to separate date and time
    parts = dt_str.split()
    if len(parts) >= 2:
        time_part = parts[-1]
        # Check if time part is in HH:MM format (5 characters with one colon)
        if len(time_part) == 5 and time_part.count(':') == 1:
            # Check if it's a valid time format (digits and colon only)
            if all(c in '0123456789:' for c in time_part):
                # Append seconds
                fixed_dt_str = ' '.join(parts[:-1]) + ' ' + time_part + ':00'
                return fixed_dt_str
    
    return dt_str


def fix_datetime_strings_vectorized(dt_series):
    """Vectorized version of datetime string fixing"""
    # Create a mask for strings that need fixing (HH:MM format without seconds)
    time_pattern = r'(\d{1,2}:\d{2})$'
    needs_fixing = dt_series.str.match(time_pattern, na=False)
    
    if needs_fixing.any():
        # Fix only the strings that need it
        fixed_series = dt_series.copy()
        fixed_series.loc[needs_fixing] = dt_series.loc[needs_fixing].str.replace(
            r'(\d{1,2}:\d{2})$', r'\1:00', regex=True
        )
        return fixed_series
    
    return dt_series


def clean_datetime_string_advanced(dt_str):
    """Advanced cleaning for problematic datetime strings"""
    if pd.isna(dt_str) or dt_str == '' or dt_str is None:
        return dt_str
    
    # Convert to string and strip
    dt_str = str(dt_str).strip()
    
    # Remove common problematic characters
    dt_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', dt_str)
    dt_str = re.sub(r'\s+', ' ', dt_str)
    dt_str = re.sub(r'["\']', '', dt_str)
    
    # Handle common issues
    # Fix missing seconds
    if re.match(r'\d{1,2}:\d{2}$', dt_str):
        dt_str += ':00'
    
    # Fix missing time
    if re.match(r'\d{1,2}/\d{1,2}/\d{4}$', dt_str):
        dt_str += ' 00:00:00'
    
    # Fix missing date
    if re.match(r'\d{1,2}:\d{2}:\d{2}$', dt_str):
        dt_str = '01/01/2000 ' + dt_str
    
    # Handle various separators
    dt_str = re.sub(r'[^\w\s:/\-\.]', ' ', dt_str)
    
    # Fix double spaces
    dt_str = re.sub(r'\s+', ' ', dt_str)
    
    return dt_str.strip()


def parse_datetime_string(dt_str, datetime_format=None):
    """Parse datetime string using the same approach as the main processing"""
    if pd.isna(dt_str) or not str(dt_str).strip():
        return pd.NaT
    
    dt_str = str(dt_str).strip()
    
    # Try using the detected format first
    if datetime_format:
        try:
            return pd.to_datetime(dt_str, format=datetime_format)
        except:
            pass
    
    # Try all known formats
    for fmt in DATETIME_FORMATS:
        try:
            return pd.to_datetime(dt_str, format=fmt)
        except:
            continue
    
    # Final fallback
    try:
        return pd.to_datetime(dt_str, errors='coerce')
    except:
        return pd.NaT


def detect_datetime_format(dt_series, sample_size=500):
    """Detect the best datetime format for a series of datetime strings"""
    # Use a smaller sample for format detection to improve speed
    sample_size = min(sample_size, len(dt_series))
    sample_data = dt_series.head(sample_size)
    
    best_format = None
    best_success_rate = 0
    
    print(f"Testing {len(DATETIME_FORMATS)} formats on {sample_size} sample rows...")
    
    # Test formats in parallel using vectorized operations
    for fmt in DATETIME_FORMATS:
        try:
            # Vectorized parsing test
            test_parsed = pd.to_datetime(sample_data, format=fmt, errors='coerce')
            success_rate = test_parsed.notna().sum() / len(sample_data)
            
            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_format = fmt
                
            # Early exit if we find a perfect match
            if success_rate == 1.0:
                print(f"Perfect match found with format: {fmt}")
                break
                
        except Exception:
            continue
    
    print(f"Best format: {best_format} (success rate: {best_success_rate:.2%})")
    return best_format, best_success_rate