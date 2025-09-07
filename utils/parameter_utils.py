"""
Parameter extraction and processing utilities.
"""
import pandas as pd
import re


def is_dxa5000_component(component):
    """Check if the component is DXA5000 or similar"""
    if pd.isna(component) or not str(component).strip():
        return False
    component_str = str(component).strip().lower()
    return 'dxa' in component_str and '5000' in component_str


def extract_parameters_from_text(text):
    """Extract parameters from text with comprehensive approach"""
    if pd.isna(text) or text == '':
        return []
    
    text = str(text).strip()
    if not text:
        return []
    
    found_parameters = []
    
    # Method 1: Direct extraction (most straightforward for TubeHistory.csv)
    if text and text.strip():
        # For TubeHistory.csv format, parameters are typically single values in the Parameters column
        param = text.strip()
        if param:
            found_parameters.append(param)
            print(f"Found parameter: '{param}'")
    
    # Method 2: Handle pipe-separated parameters (if any)
    if '|' in text:
        parts = [part.strip() for part in text.split('|') if part.strip()]
        for part in parts:
            if '=' in part:
                key, _ = part.split('=', 1)
                param = key.strip()
                if param:
                    found_parameters.append(param)
                    print(f"Found parameter from pipe-separated: '{param}'")
            else:
                if part:
                    found_parameters.append(part)
                    print(f"Found parameter from pipe-separated: '{part}'")
    
    # Method 3: Handle key-value pairs with equals sign
    kv_pairs = re.findall(r'([^=,\s]+)\s*=\s*([^,\s]+)', text)
    for key, value in kv_pairs:
        if key and key not in found_parameters:
            found_parameters.append(key)
            print(f"Found parameter from key-value: '{key}'")
    
    # Clean parameters and remove duplicates
    seen = set()
    unique_params = []
    
    for param in found_parameters:
        # Remove any remaining datetime patterns
        param = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?|\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}(?::\d{2})?', '', param)
        param = param.strip()
        
        # Additional cleaning for common patterns
        param = re.sub(r'^[^\w]+|[^\w]+$', '', param)  # Remove non-alphanumeric chars from start/end
        param = re.sub(r'\s+', ' ', param).strip()  # Replace multiple spaces with single space
        
        # DEBUG: Print all parameters being processed
        print(f"Processing parameter: '{param}'")
        
        # Check if the parameter should be filtered
        if param.lower() == 'ahm':
            print(f"Filtered out parameter 'ahm': {param}")
        elif 'dxa' in param.lower() and '5000' in param.lower():  # Filter out DXA5000
            print(f"Filtered out DXA5000 parameter: {param}")
        elif not param:
            print(f"Filtered out empty parameter: '{param}'")
        elif len(param) <= 1:
            print(f"Filtered out parameter with length <= 1: '{param}'")
        elif param in seen:
            print(f"Filtered out duplicate parameter: {param}")
        else:
            seen.add(param)
            unique_params.append(param)
            print(f"Added parameter: {param}")
            
            # Specifically log I_ parameters
            if param.startswith('I_'):
                print(f"*** FOUND I_ PARAMETER: {param} ***")
    
    return unique_params


def get_missing_events(tube_created_time, upload_time, arrived_time, download_time, loaded_time):
    """Get list of missing events for incomplete samples"""
    missing = []
    if tube_created_time is None:
        missing.append("Tube Created")
    if upload_time is None:
        missing.append("Host Upload")
    if arrived_time is None:
        missing.append("Arrived at Input")
    if download_time is None:
        missing.append("Instrument Download")
    if loaded_time is None:
        missing.append("Loaded Into Storage")
    return "; ".join(missing) if missing else "None"


def get_incomplete_reason(tube_created_time, upload_time, arrived_time, download_time, loaded_time):
    """Get detailed reason why sample is incomplete"""
    if tube_created_time is None and upload_time is None:
        return "Missing both Tube Created and Host Upload events"
    elif tube_created_time is None:
        return "Missing Tube Created event"
    elif upload_time is None:
        return "Missing Host Upload event"
    else:
        return "Missing other critical events"