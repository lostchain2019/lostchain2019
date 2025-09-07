"""
CSV loading and parsing functionality.
"""
import os
import csv
import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_utils import count_lines, detect_file_format, split_line_with_delimiter


class MultiCSVLoaderThread(QThread):
    """Enhanced thread for loading multiple CSV files with robust parsing"""
    progress_updated = pyqtSignal(int)
    loading_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths  # List of file paths
        self.total_files = len(file_paths)
        self.current_file_index = 0
        self._is_running = True
    
    def run(self):
        try:
            all_data = []
            total_lines_all_files = 0
            processed_lines_all_files = 0
            
            # First, count total lines in all files for progress tracking
            print("Counting total lines in all files...")
            for file_path in self.file_paths:
                lines_in_file = count_lines(file_path)
                total_lines_all_files += lines_in_file
                print(f"File {file_path}: {lines_in_file} lines")
            
            print(f"Total lines to process: {total_lines_all_files}")
            
            # Process each file
            for file_index, file_path in enumerate(self.file_paths):
                if not self._is_running:
                    break
                    
                self.current_file_index = file_index
                file_progress_start = (file_index / self.total_files) * 100
                file_progress_end = ((file_index + 1) / self.total_files) * 100
                
                print(f"\nProcessing file {file_index + 1}/{self.total_files}: {file_path}")
                
                # Enhanced delimiter and encoding detection
                delimiter, encoding, datetime_column = detect_file_format(file_path)
                print(f"Detected: delimiter='{delimiter}', encoding='{encoding}', datetime_column='{datetime_column}'")
                
                # Parse the file with progress tracking
                try:
                    df, lines_processed = self._parse_file_with_progress(
                        file_path, delimiter, encoding, datetime_column,
                        processed_lines_all_files, total_lines_all_files,
                        file_progress_start, file_progress_end
                    )
                    
                    if df is not None and not df.empty:
                        all_data.append(df)
                        processed_lines_all_files += lines_processed
                        print(f"Successfully parsed {len(df)} rows from {file_path}")
                    else:
                        print(f"No data extracted from {file_path}")
                
                except Exception as e:
                    print(f"Error parsing {file_path}: {str(e)}")
                    # Continue with next file instead of failing completely
                    continue
                
                # Update progress after each file
                overall_progress = (processed_lines_all_files / total_lines_all_files) * 100
                self.progress_updated.emit(int(overall_progress))
            
            # Combine all data
            if all_data and self._is_running:
                combined_df = pd.concat(all_data, ignore_index=True)
                print(f"\nSuccessfully combined {len(all_data)} files into {len(combined_df)} total rows")
            else:
                combined_df = pd.DataFrame()
                print("\nNo data extracted from any file")
            
            # Final progress update
            self.progress_updated.emit(100)
            self.loading_complete.emit(combined_df)
            
        except Exception as e:
            error_msg = f"Failed to load files: {str(e)}"
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            self.error_occurred.emit(error_msg)
    
    def stop(self):
        """Stop the thread gracefully"""
        self._is_running = False
        self.wait()
    
    def _parse_file_with_progress(self, file_path, delimiter, encoding, datetime_column,
                                 global_processed_lines, global_total_lines,
                                 file_progress_start, file_progress_end):
        """Parse a single file with detailed progress tracking"""
        data = []
        lines_in_file = 0
        lines_processed_in_file = 0
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                # Read header
                header_line = f.readline().strip()
                lines_in_file += 1
                lines_processed_in_file += 1
                
                if header_line.startswith('\ufeff'):
                    header_line = header_line[1:]
                
                # Split header by detected delimiter
                header_fields = split_line_with_delimiter(header_line, delimiter)
                
                # Determine column format based on number of columns
                if len(header_fields) == 6:
                    column_names = ['Sample ID', 'Component', 'Event', 'Priority', 'Parameters', datetime_column]
                elif len(header_fields) == 7:
                    # This is likely the invalid datetime format
                    column_names = ['Original_Index', 'Sample ID', 'Component', 'Event', 'Priority', 'Parameters', 'Original_DateTime_String']
                elif len(header_fields) == 10:
                    column_names = ['Date', 'Sample ID', 'Component', 'Event', 'Pos.', 'Comment', 'Priority', 'Parameters', 'Result', 'Comment2']
                else:
                    # Handle variable columns more flexibly
                    if len(header_fields) >= 6:
                        column_names = header_fields[:6]
                        # Ensure datetime column is included
                        if datetime_column not in column_names:
                            column_names[-1] = datetime_column
                    elif len(header_fields) >= 4:
                        # Minimum required columns
                        column_names = header_fields[:4]
                        # Add missing columns with defaults
                        while len(column_names) < 6:
                            if len(column_names) == 4:
                                column_names.append('Priority')
                            elif len(column_names) == 5:
                                column_names.append('Parameters')
                            else:
                                column_names.append(datetime_column)
                    else:
                        # Very few columns - try to work with what we have
                        column_names = header_fields
                        # Pad with defaults
                        defaults = ['Sample ID', 'Component', 'Event', 'Priority', 'Parameters', datetime_column]
                        while len(column_names) < 6:
                            column_names.append(defaults[len(column_names)])
                    
                    print(f"Using flexible column mapping: {column_names}")
                
                print(f"Header columns: {len(header_fields)} -> {column_names}")
                
                # Process data lines
                for line_num, line in enumerate(f, 2):  # Start from line 2 (after header)
                    if not self._is_running:
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                    
                    lines_in_file += 1
                    lines_processed_in_file += 1
                    
                    # Split line by detected delimiter
                    fields = split_line_with_delimiter(line, delimiter)
                    
                    # Handle variable number of fields with better error handling
                    try:
                        if len(fields) == len(column_names):
                            row_data = dict(zip(column_names, fields))
                        elif len(fields) > len(column_names):
                            # Take the first N fields
                            row_data = dict(zip(column_names, fields[:len(column_names)]))
                        else:
                            # Pad with empty strings
                            padded_fields = fields + [''] * (len(column_names) - len(fields))
                            row_data = dict(zip(column_names, padded_fields))
                        
                        # Validate that we have essential data
                        if row_data.get('Sample ID', '').strip():
                            data.append(row_data)
                        else:
                            print(f"Skipping line {line_num}: No Sample ID found")
                            
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
                        print(f"Line content: {line[:100]}...")
                        continue
                    
                    # Update progress periodically (every 100 lines or for small files)
                    if lines_processed_in_file % 100 == 0 or lines_processed_in_file == lines_in_file:
                        # Calculate overall progress
                        overall_progress = ((global_processed_lines + lines_processed_in_file) / global_total_lines) * 100
                        self.progress_updated.emit(int(overall_progress))
                
                # Create DataFrame
                df = pd.DataFrame(data)
                print(f"Extracted {len(df)} rows from {lines_processed_in_file} lines")
                
                # Validate the DataFrame
                if len(df) == 0:
                    print("Warning: No data extracted from file")
                    return None, lines_processed_in_file
                
                # Check for required columns
                required_columns = ['Sample ID']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"Warning: Missing required columns: {missing_columns}")
                
                # Check data quality
                sample_id_count = df['Sample ID'].nunique() if 'Sample ID' in df.columns else 0
                print(f"Data quality: {len(df)} rows, {sample_id_count} unique samples")
                
                return df, lines_processed_in_file
                
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
            raise