"""
File handling utilities for CSV parsing and file operations.
"""
import os
import csv
from config.constants import CSV_ENCODINGS, CSV_DELIMITERS
from config.dependencies import CHARDET_AVAILABLE


def count_lines(file_path):
    """Count total lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        try:
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0


def detect_file_format(file_path):
    """Enhanced detection of delimiter, encoding, and datetime column with better error handling"""
    print(f"Detecting format for file: {file_path}")
    
    # Try to detect encoding first
    detected_encoding = 'utf-8'
    for encoding in CSV_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                first_line = f.readline()
                if first_line and len(first_line.strip()) > 0:
                    detected_encoding = encoding
                    print(f"Detected encoding: {encoding}")
                    break
        except (UnicodeDecodeError, IOError) as e:
            print(f"Failed to read with encoding {encoding}: {e}")
            continue
    
    # Now detect delimiter and datetime column
    try:
        with open(file_path, 'r', encoding=detected_encoding, errors='ignore') as f:
            first_line = f.readline().strip()
            if not first_line:
                raise Exception("File appears to be empty or contains only whitespace")
            
            if first_line.startswith('\ufeff'):
                first_line = first_line[1:]
            
            print(f"Header line: {first_line[:100]}...")
            
            # Try each delimiter
            best_delimiter = None
            best_field_count = 0
            
            for delimiter in CSV_DELIMITERS:
                fields = first_line.split(delimiter)
                field_count = len(fields)
                print(f"Delimiter '{delimiter}': {field_count} fields")
                
                # Prefer delimiters that give us reasonable field counts
                if field_count >= 3:  # At least 3 fields
                    if field_count > best_field_count:
                        best_field_count = field_count
                        best_delimiter = delimiter
            
            if best_delimiter:
                delimiter = best_delimiter
                fields = first_line.split(delimiter)
                print(f"Selected delimiter '{delimiter}' with {len(fields)} fields")
                
                # Check if we have a datetime column
                datetime_column = None
                for field in fields:
                    field_lower = field.lower().strip()
                    if any(dt_keyword in field_lower for dt_keyword in ['date', 'time', 'datetime']):
                        datetime_column = field.strip('"\'')
                        break
                
                # If no obvious datetime column found, use the last column
                if not datetime_column:
                    datetime_column = fields[-1].strip('"\'')
                
                print(f"Detected datetime column: {datetime_column}")
                return delimiter, detected_encoding, datetime_column
            else:
                raise Exception("Could not detect a suitable delimiter")
                
    except Exception as e:
        print(f"Error in file format detection: {e}")
        # Fallback with more lenient settings
        return ',', 'utf-8', 'DateTime'


def detect_delimiter_and_encoding(file_path):
    """Detect the delimiter and encoding for a CSV file"""
    for encoding in CSV_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline()
                if first_line.startswith('\ufeff'):
                    first_line = first_line[1:]
                
                for delimiter in [';', ',']:
                    fields = first_line.split(delimiter)
                    if len(fields) >= 6:  # We need at least 6 columns
                        return delimiter, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    # If all else fails, try to analyze the file more thoroughly
    if CHARDET_AVAILABLE:
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)  # Read first 1KB
                
            # Try to detect encoding
            import chardet
            detected = chardet.detect(raw_data)
            print(f"Detected encoding: {detected}")
            
            if detected['confidence'] > 0.7:
                try:
                    with open(file_path, 'r', encoding=detected['encoding']) as f:
                        first_line = f.readline()
                        if first_line.startswith('\ufeff'):
                            first_line = first_line[1:]
                        
                        for delimiter in [';', ',']:
                            fields = first_line.split(delimiter)
                            if len(fields) >= 6:
                                return delimiter, detected['encoding']
                except:
                    pass
        except Exception as e:
            print(f"Error in enhanced delimiter detection: {str(e)}")
    
    # Final fallback
    print("Using default delimiter and encoding")
    return ';', 'utf-8'  # Default to semicolon


def split_line_with_delimiter(line, delimiter):
    """Split a line by delimiter, handling quoted fields"""
    if delimiter not in line:
        return [line]
    
    # Use csv module for proper quote handling
    try:
        reader = csv.reader([line], delimiter=delimiter, quotechar='"')
        return next(reader)
    except:
        # Fallback to simple split
        fields = line.split(delimiter)
        # Clean each field
        cleaned_fields = []
        for field in fields:
            field = field.strip().strip('"').strip("'")
            cleaned_fields.append(field)
        return cleaned_fields


def validate_file_path(file_path, max_size_mb=100):
    """Validate a file path and check size"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Check file sizes
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    if file_size > max_size_mb:
        return False, f"File is large ({file_size:.1f} MB)"
    
    return True, f"File size: {file_size:.1f} MB"