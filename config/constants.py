"""
Configuration and constants for the Laboratory TAT Analysis Application.
"""
import csv

# Set CSV field size limit to 100MB
csv.field_size_limit(100 * 1024 * 1024)

# Define a palette of unique colors for buttons
BUTTON_COLORS = [
    "#4CAF50",  # Green
    "#2196F3",  # Blue
    "#FF9800",  # Orange
    "#9C27B0",  # Purple
    "#F44336",  # Red
    "#00BCD4",  # Cyan
    "#795548",  # Brown
    "#607D8B",  # Blue Grey
    "#E91E63",  # Pink
    "#009688",  # Teal
    "#8BC34A",  # Light Green
    "#FFC107",  # Amber
    "#3F51B5",  # Indigo
    "#CDDC39",  # Lime
    "#FF5722",  # Deep Orange
    "#673AB7",  # Deep Purple
    "#3F51B5",  # Indigo
    "#009688",  # Teal
    "#FF5722",  # Deep Orange
    "#795548",  # Brown
]

# Datetime format patterns for parsing
DATETIME_FORMATS = [
    # Most common formats first for better performance
    '%m/%d/%Y %H:%M:%S',  # MM/DD/YYYY HH:MM:SS
    '%m/%d/%Y %H:%M',      # MM/DD/YYYY HH:MM
    '%d/%m/%Y %H:%M:%S',  # DD/MM/YYYY HH:MM:SS
    '%d/%m/%Y %H:%M',      # DD/MM/YYYY HH:MM
    '%Y-%m-%d %H:%M:%S',  # ISO format
    '%Y-%m-%d %H:%M',     # ISO format without seconds
    '%m/%d/%y %H:%M:%S',   # Two-digit year
    '%m/%d/%y %H:%M',     # Two-digit year without seconds
    '%d/%m/%y %H:%M:%S',   # Day first, two-digit year
    '%d/%m/%y %H:%M',     # Day first, two-digit year without seconds
    '%m-%d-%Y %H:%M:%S',  # Different separator
    '%m-%d-%Y %H:%M',     # Different separator without seconds
    '%d-%m-%Y %H:%M:%S',  # Day first, different separator
    '%d-%m-%Y %H:%M',     # Day first, different separator without seconds
    '%Y/%m/%d %H:%M:%S',  # ISO with slashes
    '%Y/%m/%d %H:%M',     # ISO with slashes without seconds
    '%m.%d.%Y %H:%M:%S',  # European format with dots
    '%m.%d.%Y %H:%M',     # European format with dots without seconds
    '%d.%m.%Y %H:%M:%S',  # European format with dots, day first
    '%d.%m.%Y %H:%M',     # European format with dots, day first without seconds
    # Additional formats that might be causing issues
    '%Y-%m-%dT%H:%M:%S',  # ISO with T separator
    '%Y-%m-%dT%H:%M:%SZ', # ISO with T and Z
    '%Y-%m-%dT%H:%M:%S.%f', # ISO with microseconds
    '%Y-%m-%dT%H:%M:%S.%fZ', # ISO with microseconds and Z
    '%m/%d/%Y %I:%M:%S %p',  # 12-hour format with AM/PM
    '%m/%d/%Y %I:%M %p',     # 12-hour format without seconds
    '%d/%m/%Y %I:%M:%S %p',  # European 12-hour format
    '%d/%m/%Y %I:%M %p',     # European 12-hour format without seconds
    '%Y%m%d %H:%M:%S',       # Compact format
    '%Y%m%d %H:%M',          # Compact format without seconds
    '%Y%m%d%H%M%S',          # No separator compact
    '%Y%m%d%H%M',            # No separator compact without seconds
    '%d-%b-%Y %H:%M:%S',     # Day-Month-Year with abbreviated month
    '%d-%b-%y %H:%M:%S',     # Day-Month-Year with abbreviated month, 2-digit year
    '%b %d %Y %H:%M:%S',     # Month Day Year
    '%d %b %Y %H:%M:%S',     # Day Month Year
    '%Y-%m-%d',              # Date only
    '%m/%d/%Y',              # Date only US format
    '%d/%m/%Y',              # Date only European format
]

# CSV parsing settings
CSV_ENCODINGS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
CSV_DELIMITERS = [';', ',', '\t', '|', ':', ' ', '~', '^']

# File size limits
MAX_FILE_SIZE_MB = 100

# UI Constants
DEFAULT_WINDOW_SIZE = (1800, 800)
DEFAULT_WINDOW_POSITION = (100, 100)

# Table column headers
TIME_ANALYSIS_HEADERS = [
    'Sample ID', 'Component', 'Parameters', 
    'Tube Created Time', 'Arrived At Input Time', 'Instrument Download Time', 'Host Upload Time',
    'Preprocessing Time (min)', 'Analytical TAT (min)', 'Total TAT (min)', 
    'Status', 'Scenario'
]

PARAMETER_STATS_HEADERS = [
    'Parameter', 'Count', 'Avg TAT (min)', 'Median TAT (min)', 'Min TAT (min)', 'Max TAT (min)'
]

# Summary statistics metrics
SUMMARY_METRICS = [
    "Total Samples",
    "Complete Samples", 
    "Incomplete Samples",
    "LIS Down Cases",
    "Direct Analysis Cases",
    "Automation Processed Samples",
    "Avg Preprocessing Time",
    "Avg Analytical TAT",
    "Avg Total TAT",
    "Median Preprocessing Time",
    "Median Analytical TAT",
    "Median Total TAT"
]

# Scenario types
SCENARIOS = {
    'NORMAL': 'Normal',
    'LIS_DOWN': 'LIS Down',
    'DIRECT_ANALYSIS': 'Direct Analysis', 
    'INCOMPLETE': 'Incomplete'
}

# Status types
STATUSES = {
    'VALID': 'Valid',
    'INVALID': 'Invalid',
    'INCOMPLETE': 'Incomplete',
    'REVIEW_DELAYED': 'Review - Delayed Sample',
    'ECSD_STORAGE': 'ECSD Storage',
    'ECSD_STORAGE_DELAYED': 'ECSD Storage - Delayed Sample',
    'ECSD_STORAGE_NO_INSTRUMENT': 'ECSD Storage - No Instrument Download',
    'NO_INSTRUMENT_DOWNLOAD': 'No Instrument Download'
}

# Event names (case-insensitive matching)
EVENTS = {
    'TUBE_CREATED': 'tube created',
    'ARRIVED_AT_INPUT': 'arrived at input',
    'INSTRUMENT_DOWNLOAD': 'instrument download',
    'HOST_UPLOAD': 'host upload',
    'LOADED_INTO_STORAGE': 'loaded into storage'
}

# Time thresholds
DELAYED_SAMPLE_THRESHOLD_MINUTES = 60

# Export file naming patterns
EXPORT_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'