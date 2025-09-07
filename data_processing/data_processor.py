"""
Main data processing logic for TAT calculations.
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from PyQt6.QtCore import QThread, pyqtSignal
from config.constants import (
    DATETIME_FORMATS, EVENTS, SCENARIOS, STATUSES, 
    DELAYED_SAMPLE_THRESHOLD_MINUTES
)
from utils.datetime_utils import (
    fix_datetime_strings_vectorized, clean_datetime_string_advanced,
    detect_datetime_format
)
from utils.parameter_utils import (
    extract_parameters_from_text, get_missing_events, 
    get_incomplete_reason, is_dxa5000_component
)


class DataProcessingThread(QThread):
    progress_updated = pyqtSignal(int, str)
    processing_complete = pyqtSignal(object, object, object, object, object, object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data):
        super().__init__()
        # Create a copy of the data to avoid SettingWithCopyWarning
        self.data = data.copy()
        self.datetime_format = None  # Cache detected datetime format
        self.automation_processed_samples = set()
        self.validated_samples = set()  # Track samples with host upload event
        self.ecsd_direct_stored_samples = set()  # Track ECSD direct stored tubes
        self.ecsd_total_loaded_samples = set()   # Track all ECSD loaded tubes
        self.incomplete_samples_data = []  # Track incomplete samples for export
        self._is_running = True
    
    def run(self):
        try:
            # Step 1: Filter rows containing 'ahm' in Component
            self.progress_updated.emit(5, "Filtering data...")
            self._filter_data()
            
            # Step 2: Parse datetime with optimized parsing
            self.progress_updated.emit(15, "Parsing datetime...")
            self._parse_datetime_optimized()
            
            # Step 3: Extract parameters and components
            self.progress_updated.emit(35, "Extracting parameters...")
            self._extract_parameters()
            
            # Step 4: Calculate times
            self.progress_updated.emit(65, "Calculating times...")
            self._calculate_times()
            
            # Step 5: Calculate parameter statistics
            self.progress_updated.emit(85, "Calculating parameter statistics...")
            self._calculate_parameter_statistics()
            
            # Step 6: Export incomplete samples
            self.progress_updated.emit(90, "Exporting incomplete samples...")
            self._export_incomplete_samples()
            
            # Step 7: Finalize
            self.progress_updated.emit(95, "Finalizing...")
            
            self.progress_updated.emit(100, "Complete")
            self.processing_complete.emit(
                self.data, 
                self.time_results, 
                self.sample_results, 
                self.sample_scenarios, 
                self.scenario_counts,
                self.parameter_stats
            )
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop the thread gracefully"""
        self._is_running = False
        self.wait()
    
    def _filter_data(self):
        """Filter rows containing 'ahm' in Component (exact match)"""
        original_rows = len(self.data)
        
        # Only filter out rows where Component is exactly 'ahm' (case-insensitive)
        if 'Component' in self.data.columns:
            # Create mask for rows where Component is not exactly 'ahm'
            mask = ~self.data['Component'].astype(str).str.lower().str.fullmatch('ahm')
            self.data = self.data[mask]
            filtered_rows = len(self.data)
            print(f"Filtered out {original_rows - filtered_rows} rows with Component exactly 'ahm'")
        else:
            print("Component column not found - skipping 'ahm' filtering")
        
        print(f"Data filtering complete. Remaining rows: {len(self.data)}")
    
    def _parse_datetime_optimized(self):
        """Highly optimized datetime parsing with vectorized operations"""
        # Determine which column contains the datetime
        datetime_column = None
        if 'DateTime' in self.data.columns:
            datetime_column = 'DateTime'
        elif 'Date' in self.data.columns:
            datetime_column = 'Date'
        elif 'Original_DateTime_String' in self.data.columns:
            datetime_column = 'Original_DateTime_String'
        else:
            print("No datetime column found in data")
            return
        
        # CRITICAL: Save original datetime strings BEFORE any conversion
        self.data.loc[:, 'Original_DateTime_String'] = self.data[datetime_column].astype(str).copy()
        
        # Check if ActualDateTime already exists and contains valid datetimes
        if 'ActualDateTime' in self.data.columns:
            valid_mask = self.data['ActualDateTime'].notna()
            if valid_mask.any():
                preserved_actual = self.data['ActualDateTime'].copy()
            else:
                preserved_actual = None
        else:
            preserved_actual = None
        
        print("Starting optimized datetime parsing...")
        
        # Vectorized string cleaning - much faster than apply()
        dt_series = self.data[datetime_column].astype(str)
        
        # Clean in one vectorized operation
        dt_series = (dt_series
                    .str.strip()
                    .str.replace(r'[\x00-\x1f\x7f-\x9f]', '', regex=True)
                    .str.replace(r'\s+', ' ', regex=True)
                    .str.replace('["\']', '', regex=True))
        
        # Fix missing seconds using vectorized operations
        dt_series = fix_datetime_strings_vectorized(dt_series)
        
        # Debug: Print sample
        print("Sample cleaned datetime strings:")
        for i in range(min(5, len(dt_series))):
            print(f"  Row {i}: '{dt_series.iloc[i]}'")
        
        # Comprehensive format detection and parsing
        best_format, best_success_rate = detect_datetime_format(dt_series)
        
        # Parse the entire dataset with the best format
        if best_format and best_success_rate > 0.3:  # Lower threshold for better coverage
            self.datetime_format = best_format
            print(f"Parsing entire dataset with format: {best_format}")
            
            # Vectorized parsing of entire dataset
            new_datetimes = pd.to_datetime(dt_series, format=best_format, errors='coerce')
            
            # If we didn't get 100% success, try to fill in missing values with other formats
            if new_datetimes.isna().any():
                missing_mask = new_datetimes.isna()
                missing_data = dt_series[missing_mask]
                
                print(f"Attempting to parse {missing_mask.sum()} remaining rows with alternative formats...")
                
                # Try alternative formats only on missing rows
                for fmt in DATETIME_FORMATS:
                    if fmt == best_format:
                        continue
                    
                    try:
                        alt_parsed = pd.to_datetime(missing_data, format=fmt, errors='coerce')
                        filled_mask = alt_parsed.notna()
                        
                        if filled_mask.any():
                            new_datetimes.loc[missing_mask & filled_mask] = alt_parsed[filled_mask]
                            missing_mask = new_datetimes.isna()
                            missing_data = dt_series[missing_mask]
                            
                            if not missing_mask.any():
                                break
                    except Exception:
                        continue
        else:
            # Fallback to pandas automatic parsing
            print("Using pandas automatic parsing as fallback...")
            try:
                new_datetimes = pd.to_datetime(dt_series, infer_datetime_format=True, errors='coerce')
            except Exception:
                new_datetimes = pd.to_datetime(dt_series, errors='coerce')
            
            # If still many failures, try additional cleaning and parsing
            total_rows = len(dt_series)
            if new_datetimes.isna().sum() > total_rows * 0.1:  # If more than 10% failed
                print("Attempting additional cleaning for failed datetime strings...")
                
                # Try to clean and parse failed strings individually
                failed_mask = new_datetimes.isna()
                failed_strings = dt_series[failed_mask]
                
                for i, dt_str in enumerate(failed_strings):
                    if i % 1000 == 0 and i > 0:
                        print(f"  Processing failed string {i}/{len(failed_strings)}")
                    
                    # Try various cleaning approaches
                    cleaned_str = clean_datetime_string_advanced(dt_str)
                    if cleaned_str != dt_str:
                        try:
                            parsed_dt = pd.to_datetime(cleaned_str, errors='coerce')
                            if not pd.isna(parsed_dt):
                                failed_indices = failed_strings.index[failed_strings == dt_str]
                                new_datetimes.loc[failed_indices] = parsed_dt
                        except Exception:
                            continue
        
        # Create ActualDateTime column
        if preserved_actual is not None:
            self.data['ActualDateTime'] = new_datetimes
            # Keep preserved values where they exist
            self.data.loc[preserved_actual.notna(), 'ActualDateTime'] = preserved_actual[preserved_actual.notna()]
        else:
            self.data['ActualDateTime'] = new_datetimes
        
        # Mark valid rows
        self.data['IsValid'] = self.data['ActualDateTime'].notna()
        
        # Print statistics
        total_rows = len(self.data)
        valid_rows = self.data['IsValid'].sum()
        success_rate = valid_rows / total_rows if total_rows > 0 else 0
        
        print(f"Datetime parsing completed:")
        print(f"  Total rows: {total_rows:,}")
        print(f"  Successfully parsed: {valid_rows:,}")
        print(f"  Success rate: {success_rate:.2%}")
        
        # Export invalid rows for debugging (only if there are many failures)
        invalid_mask = self.data['ActualDateTime'].isna()
        if invalid_mask.sum() > 0:
            invalid_count = invalid_mask.sum()
            print(f"  Failed to parse: {invalid_count:,} rows")
            
            # Show sample of failed datetime strings for debugging
            invalid_samples = self.data[invalid_mask]['Original_DateTime_String'].head(10)
            print(f"  Sample of failed datetime strings:")
            for i, dt_str in enumerate(invalid_samples):
                print(f"    {i+1}: '{dt_str}'")
        
        # Drop rows with invalid datetime
        self.data = self.data.dropna(subset=['ActualDateTime'])
        
        # Check for required events
        if 'Event' in self.data.columns:
            self.data.loc[:, 'Event'] = self.data['Event'].fillna('').astype(str)
            self.data.loc[:, 'Event_Lower'] = self.data['Event'].str.lower()
    
    def _extract_parameters(self):
        """Extract parameters from data"""
        # This will be handled during time calculation
        pass
    
    def _calculate_times(self):
        """Calculate times for each sample with updated logic according to help section"""
        # Get sample start times using optimized groupby
        tube_created = self.data[self.data['Event_Lower'] == EVENTS['TUBE_CREATED']].groupby('Sample ID')['ActualDateTime'].min()
        arrived_at_input = self.data[self.data['Event_Lower'] == EVENTS['ARRIVED_AT_INPUT']].groupby('Sample ID')['ActualDateTime'].min()
        instrument_download = self.data[self.data['Event_Lower'] == EVENTS['INSTRUMENT_DOWNLOAD']].groupby('Sample ID')['ActualDateTime'].min()
        host_upload = self.data[self.data['Event_Lower'] == EVENTS['HOST_UPLOAD']].groupby('Sample ID')['ActualDateTime'].min()
        loaded_into_storage = self.data[self.data['Event_Lower'] == EVENTS['LOADED_INTO_STORAGE']].groupby('Sample ID')['ActualDateTime'].min()
        
        # Get all unique sample IDs from the data (no event restrictions)
        all_sample_ids = set(self.data['Sample ID'].unique())
        
        # Get all components using vectorized operations (no restrictions)
        instrument_components = {}
        for sample_id in all_sample_ids:
            sample_data = self.data[self.data['Sample ID'] == sample_id]
            # Get all components, including those that might be 'LIS' or empty
            components = sample_data['Component'].unique()
            instrument_components[sample_id] = components
        
        # Get parameters using optimized approach
        sample_component_parameters = {}
        for sample_id in all_sample_ids:
            sample_data = self.data[self.data['Sample ID'] == sample_id]
            for component in instrument_components.get(sample_id, []):
                param_data = sample_data[
                    (sample_data['Component'] == component) & 
                    (sample_data['Parameters'].notna()) & 
                    (sample_data['Parameters'] != '')
                ]
                
                all_params = []
                for _, row in param_data.iterrows():
                    params = extract_parameters_from_text(row['Parameters'])
                    for param in params:
                        if param and param not in all_params:
                            all_params.append(param)
                
                sample_component_parameters[(sample_id, component)] = all_params
        
        # Initialize results
        self.time_results = []
        self.sample_results = []
        self.sample_scenarios = {}
        self.scenario_counts = {
            SCENARIOS['NORMAL']: 0, 
            SCENARIOS['LIS_DOWN']: 0, 
            SCENARIOS['DIRECT_ANALYSIS']: 0, 
            SCENARIOS['INCOMPLETE']: 0
        }
        
        # Calculate times for each sample with updated calculations
        # Use all_sample_ids to ensure we process each sample only once
        for sample_id in all_sample_ids:
            tube_created_time = tube_created.get(sample_id, None)
            arrived_time = arrived_at_input.get(sample_id, None)
            inst_dl_time = instrument_download.get(sample_id, None)
            upload_time = host_upload.get(sample_id, None)
            loaded_time = loaded_into_storage.get(sample_id, None)
            
            # Track validated samples (those with host upload event)
            if upload_time is not None:
                self.validated_samples.add(sample_id)
            
            # Initialize variables
            total_tat_time = None
            preprocessing_time = None
            analytical_tat_time = None
            scenario = SCENARIOS['INCOMPLETE']
            status = STATUSES['INCOMPLETE']
            
            # SCENARIO DECISION TREE IMPLEMENTATION
            # Step 1: Does the sample have both "Tube Created" and "Host Upload" events?
            if tube_created_time is not None and upload_time is not None:
                # Calculate total TAT (always calculated when both events exist)
                total_tat_time = (upload_time - tube_created_time).total_seconds() / 60
                
                # Step 2: Is "Arrived At Input" time before "Tube Created" time?
                if arrived_time is not None and arrived_time < tube_created_time:
                    # LIS Down scenario
                    preprocessing_time = None
                    analytical_tat_time = None
                    scenario = SCENARIOS['LIS_DOWN']
                    status = STATUSES['INVALID']
                    
                    # NOTE: If "Arrived At Input" is also before "Host Upload", mark as automation processed
                    if arrived_time < upload_time:
                        self.automation_processed_samples.add(sample_id)
                else:
                    # Step 3: Is "Arrived At Input" time between "Tube Created" and "Host Upload"?
                    if arrived_time is not None and tube_created_time <= arrived_time <= upload_time:
                        # Normal scenario
                        preprocessing_time = (arrived_time - tube_created_time).total_seconds() / 60
                        analytical_tat_time = (upload_time - arrived_time).total_seconds() / 60
                        scenario = SCENARIOS['NORMAL']
                        
                        # Check for Delayed Sample
                        if preprocessing_time > DELAYED_SAMPLE_THRESHOLD_MINUTES:
                            status = STATUSES['REVIEW_DELAYED']
                        else:
                            status = STATUSES['VALID']
                        
                        # Mark as automation processed
                        self.automation_processed_samples.add(sample_id)
                    else:
                        # Step 4: Is "Instrument Download" time available?
                        if inst_dl_time is not None:
                            # Direct Analysis scenario with Instrument Download
                            preprocessing_time = (inst_dl_time - tube_created_time).total_seconds() / 60
                            analytical_tat_time = (upload_time - inst_dl_time).total_seconds() / 60
                            scenario = SCENARIOS['DIRECT_ANALYSIS']
                            
                            # Determine status based on "Arrived At Input"
                            if arrived_time is not None and arrived_time > upload_time:
                                # ECSD Storage case
                                status = STATUSES['ECSD_STORAGE']
                                if preprocessing_time > DELAYED_SAMPLE_THRESHOLD_MINUTES:
                                    status = STATUSES['ECSD_STORAGE_DELAYED']
                                
                                # Mark as ECSD direct stored
                                self.ecsd_direct_stored_samples.add(sample_id)
                            else:
                                # Direct Analysis without arrived_at_input or arrived_at_input not in valid range
                                status = STATUSES['VALID']
                                if preprocessing_time > DELAYED_SAMPLE_THRESHOLD_MINUTES:
                                    status = STATUSES['REVIEW_DELAYED']
                        else:
                            # Direct Analysis scenario without Instrument Download
                            if arrived_time is not None and arrived_time > upload_time:
                                # ECSD Storage without instrument download
                                scenario = SCENARIOS['DIRECT_ANALYSIS']
                                status = STATUSES['ECSD_STORAGE_NO_INSTRUMENT']
                                preprocessing_time = None
                                analytical_tat_time = None
                                
                                # Mark as ECSD direct stored
                                self.ecsd_direct_stored_samples.add(sample_id)
                            else:
                                # No arrived_at_input and no instrument download
                                scenario = SCENARIOS['DIRECT_ANALYSIS']
                                status = STATUSES['NO_INSTRUMENT_DOWNLOAD']
                                preprocessing_time = None
                                analytical_tat_time = None
            else:
                # Incomplete case - missing either tube created or host upload or both
                scenario = SCENARIOS['INCOMPLETE']
                status = STATUSES['INCOMPLETE']
                
                # Collect incomplete sample data for export
                incomplete_data = {
                    'Sample ID': sample_id,
                    'Tube Created Time': tube_created_time,
                    'Host Upload Time': upload_time,
                    'Arrived at Input Time': arrived_time,
                    'Instrument Download Time': inst_dl_time,
                    'Loaded Into Storage Time': loaded_time,
                    'Missing Events': get_missing_events(tube_created_time, upload_time, arrived_time, inst_dl_time, loaded_time),
                    'Reason': get_incomplete_reason(tube_created_time, upload_time, arrived_time, inst_dl_time, loaded_time)
                }
                self.incomplete_samples_data.append(incomplete_data)
            
            # Step 5: If "Loaded Into Storage" event exists: mark as ECSD total loaded
            if loaded_time is not None:
                self.ecsd_total_loaded_samples.add(sample_id)
            
            self.sample_scenarios[sample_id] = scenario
            self.scenario_counts[scenario] = self.scenario_counts.get(scenario, 0) + 1
            
            sample_result = {
                'Sample ID': sample_id,
                'Tube Created Time': tube_created_time,
                'Arrived At Input Time': arrived_time,
                'Instrument Download Time': inst_dl_time,
                'Host Upload Time': upload_time,
                'Preprocessing Time (min)': preprocessing_time,
                'Analytical TAT (min)': analytical_tat_time,
                'Total TAT (min)': total_tat_time,
                'Status': status,
                'Scenario': scenario
            }
            self.sample_results.append(sample_result)
            
            # Add detailed results for each component
            if sample_id in instrument_components and len(instrument_components[sample_id]) > 0:
                for component in instrument_components[sample_id]:
                    params = sample_component_parameters.get((sample_id, component), [])
                    
                    if params:
                        for param in params:
                            self.time_results.append({
                                'Sample ID': sample_id,
                                'Component': component,
                                'Parameters': param,
                                'Tube Created Time': tube_created_time,
                                'Arrived At Input Time': arrived_time,
                                'Instrument Download Time': inst_dl_time,
                                'Host Upload Time': upload_time,
                                'Preprocessing Time (min)': round(preprocessing_time, 2) if preprocessing_time is not None else None,
                                'Analytical TAT (min)': round(analytical_tat_time, 2) if analytical_tat_time is not None else None,
                                'Total TAT (min)': round(total_tat_time, 2) if total_tat_time is not None else None,
                                'Status': status,
                                'Scenario': scenario
                            })
                    else:
                        # Show all components, including LIS and empty ones, but skip DXA5000 as parameter
                        if is_dxa5000_component(component):
                            param_display = "No Parameters"
                        else:
                            param_display = component if component and component.strip() else "No Parameters"
                        
                        self.time_results.append({
                            'Sample ID': sample_id,
                            'Component': component,
                            'Parameters': param_display,
                            'Tube Created Time': tube_created_time,
                            'Arrived At Input Time': arrived_time,
                            'Instrument Download Time': inst_dl_time,
                            'Host Upload Time': upload_time,
                            'Preprocessing Time (min)': round(preprocessing_time, 2) if preprocessing_time is not None else None,
                            'Analytical TAT (min)': round(analytical_tat_time, 2) if analytical_tat_time is not None else None,
                            'Total TAT (min)': round(total_tat_time, 2) if total_tat_time is not None else None,
                            'Status': status,
                            'Scenario': scenario
                        })
            else:
                self.time_results.append({
                    'Sample ID': sample_id,
                    'Component': "Unknown",
                    'Parameters': "No Parameters",
                    'Tube Created Time': tube_created_time,
                    'Arrived At Input Time': arrived_time,
                    'Instrument Download Time': inst_dl_time,
                    'Host Upload Time': upload_time,
                    'Preprocessing Time (min)': round(preprocessing_time, 2) if preprocessing_time is not None else None,
                    'Analytical TAT (min)': round(analytical_tat_time, 2) if analytical_tat_time is not None else None,
                    'Total TAT (min)': round(total_tat_time, 2) if total_tat_time is not None else None,
                    'Status': status,
                    'Scenario': scenario
                })
    
    def _calculate_parameter_statistics(self):
        """Calculate average and median TAT for each parameter"""
        # Create a DataFrame from time_results for easier calculations
        time_df = pd.DataFrame(self.time_results)
        
        # Filter out rows with no Analytical TAT (LIS Down cases)
        valid_tat_df = time_df[time_df['Analytical TAT (min)'].notna()]
        
        # Group by parameter and calculate statistics
        parameter_stats = []
        
        if not valid_tat_df.empty:
            # Group by Parameters
            grouped = valid_tat_df.groupby('Parameters')['Analytical TAT (min)']
            
            for param_name, tat_values in grouped:
                # Calculate statistics
                count = len(tat_values)
                avg_tat = tat_values.mean()
                median_tat = tat_values.median()
                min_tat = tat_values.min()
                max_tat = tat_values.max()
                
                parameter_stats.append({
                    'Parameter': param_name,
                    'Count': count,
                    'Avg TAT (min)': round(avg_tat, 2),
                    'Median TAT (min)': round(median_tat, 2),
                    'Min TAT (min)': round(min_tat, 2),
                    'Max TAT (min)': round(max_tat, 2)
                })
        
        # Sort by average TAT (descending)
        self.parameter_stats = sorted(parameter_stats, key=lambda x: x['Avg TAT (min)'], reverse=True)
    
    def _export_incomplete_samples(self):
        """Export incomplete samples to CSV file"""
        if not self.incomplete_samples_data:
            print("No incomplete samples to export")
            return
        
        try:
            # Create DataFrame from incomplete samples
            incomplete_df = pd.DataFrame(self.incomplete_samples_data)
            
            # Generate filename with timestamp
            from datetime import datetime
            from config.constants import EXPORT_TIMESTAMP_FORMAT
            timestamp = datetime.now().strftime(EXPORT_TIMESTAMP_FORMAT)
            filename = f"incomplete_samples_{timestamp}.csv"
            
            # Export to CSV
            incomplete_df.to_csv(filename, index=False)
            
            print(f"Exported {len(incomplete_df)} incomplete samples to {filename}")
            print(f"Incomplete samples breakdown:")
            print(f"  Total incomplete samples: {len(incomplete_df)}")
            
            # Show breakdown by missing events
            if 'Missing Events' in incomplete_df.columns:
                missing_events_counts = incomplete_df['Missing Events'].value_counts()
                print(f"  Missing events breakdown:")
                for events, count in missing_events_counts.items():
                    print(f"    {events}: {count} samples")
            
            # Show breakdown by reason
            if 'Reason' in incomplete_df.columns:
                reason_counts = incomplete_df['Reason'].value_counts()
                print(f"  Reason breakdown:")
                for reason, count in reason_counts.items():
                    print(f"    {reason}: {count} samples")
                    
        except Exception as e:
            print(f"Error exporting incomplete samples: {str(e)}")
            import traceback
            print(traceback.format_exc())