"""
Help dialog with comprehensive TAT calculation documentation.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
from PyQt6.QtGui import QFont
from .base_dialogs import BaseDialog


class HelpDialog(BaseDialog):
    """Comprehensive help dialog explaining TAT calculations"""
    def __init__(self, parent=None):
        super().__init__("TAT Calculation Help", parent, 800, 600)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        help_text = """
        Laboratory TAT Analysis Application - Comprehensive Guide
        *******************************************************
        
        Table of Contents:
        1. Introduction
        2. TAT Calculation Methodology
        3. Scenarios and Special Cases
        4. Data Management
        5. Dashboard and Analysis
        6. Export and Reporting
        7. Advanced Features
        
        1. Introduction
        ***************
        
        This application is designed to analyze laboratory sample processing times by calculating 
        Turnaround Time (TAT) metrics from CSV data containing sample events. It helps laboratories 
        monitor workflow efficiency, identify bottlenecks, and optimize processes.
        
        Key Features:
        - Multi-file data loading and accumulation
        - Comprehensive TAT calculations
        - Scenario-based analysis
        - Interactive dashboard with visualizations
        - Advanced filtering and exclusion options
        - Export capabilities (PDF, CSV)
        - Raw data editing capabilities
        
        2. TAT Calculation Methodology
        ******************************
        
        The application calculates three key TAT metrics:
        
        a) Preprocessing Time:
           - Time between "Tube Created" and "Arrived At Input"
           - Formula: Preprocessing Time = Arrived At Input Time - Tube Created Time
        
        b) Analytical TAT:
           - Time between "Arrived At Input" and "Host Upload"
           - Formula: Analytical TAT = Host Upload Time - Arrived At Input Time
           - This calculation is only valid when the "Arrived At Input" event occurs BETWEEN 
             the "Tube Created" and "Host Upload" events
        
        c) Total TAT:
           - Time between "Tube Created" and "Host Upload"
           - Formula: Total TAT = Host Upload Time - Tube Created Time
        
        3. Scenarios and Special Cases
        ******************************
        
        The application implements a sophisticated decision tree to handle different scenarios:
        
        a) Normal Scenario:
           - "Arrived At Input" occurs between "Tube Created" and "Host Upload"
           - Full TAT calculation using Arrived At Input time
           - Status: "Valid" or "Review - Delayed Sample" (if preprocessing > 60 min)
           - Marked as automation processed
        
        b) LIS Down Scenario:
           - "Arrived At Input" occurs BEFORE "Tube Created" time
           - Indicates system timing issues or LIS downtime
           - NO TAT calculations are performed for these cases
           - All time fields are set to None/NA
           - Status is marked as "Invalid" with "LIS Down" scenario
           - These cases are EXCLUDED from all statistical calculations
           - If "Arrived At Input" is also before "Host Upload", the sample is included in 
             Automation Processed Samples statistics
        
        c) Direct Analysis Scenario:
           - "Arrived At Input" is NOT between "Tube Created" and "Host Upload"
           - This includes cases where:
             * "Arrived At Input" is after "Host Upload" (ECSD Storage)
             * "Arrived At Input" does not exist
             * "Arrived At Input" is before "Tube Created" (already handled as LIS Down)
        
           Subcases:
           - With "Instrument Download" time available:
             * Preprocessing Time = Instrument Download Time - Tube Created Time
             * Analytical TAT = Host Upload Time - Instrument Download Time
             * Scenario marked as "Direct Analysis"
             * Status depends on the specific case:
               - If "Arrived At Input" is after "Host Upload": "ECSD Storage" or "ECSD Storage - Delayed Sample"
               - Otherwise: "Valid" or "Review - Delayed Sample"
           
           - Without "Instrument Download" time:
             * If "Arrived At Input" is after "Host Upload": 
               - Status = "ECSD Storage - No Instrument Download"
               - Scenario = "Direct Analysis"
               - TAT calculations cannot be performed (times set to None)
             * Otherwise:
               - Status = "No Instrument Download"
               - Scenario = "Direct Analysis"
               - TAT calculations cannot be performed (times set to None)
        
        d) Incomplete Scenario:
           - Missing either "Tube Created" or "Host Upload" events
           - Status = "Incomplete"
           - These samples are excluded from most statistics and visualizations
           - Can be exported separately for further analysis
        
        Special Cases Handling:
        
        a) Delayed Sample Flag:
           - When Preprocessing Time exceeds 60 minutes
           - TAT calculations ARE performed normally
           - Status is changed to include "Delayed Sample" (e.g., "ECSD Storage - Delayed Sample")
           - These are INCLUDED in all statistical calculations
        
        b) Automation Processed Samples:
           - A sample is considered automation processed if:
             * It has an "Arrived At Input" event that occurs AFTER the "Tube Created" time 
               and BEFORE the "Host Upload" time (normal case)
             * It has an "Arrived At Input" event that occurs BEFORE the "Tube Created" time 
               AND BEFORE the "Host Upload" time (LIS Down case)
           - These samples are tracked separately for automation efficiency analysis
        
        c) Validated Samples:
           - Samples that have a "Host Upload" event are considered validated
           - These samples have completed the full laboratory process
           - This metric helps track the completeness of sample processing
        
        4. Data Management
        ******************
        
        a) Data Loading:
           - Supports loading multiple CSV files simultaneously
           - Automatically detects delimiter and encoding
           - Accumulates data from multiple files while avoiding duplicates
           - Shows progress during loading and processing
           - Handles large files efficiently with multi-threaded processing
        
        b) Raw Data Editing:
           - View and edit raw data directly in the Raw Data tab
           - Add or delete rows as needed
           - Invalid datetime records are highlighted in red
           - Update calculations after making changes
        
        c) Data Correction:
           - Load corrected CSV files to update specific datetime values
           - Tracks all corrections with detailed information
           - View correction details in a dedicated tab
           - Re-processes data automatically after corrections
        
        d) Time Adjustment:
           - Adjust "Arrived At Input" times by adding or subtracting hours
           - Useful for system-wide time corrections
           - Recalculates all TAT metrics after adjustment
        
        5. Dashboard and Analysis
        ***********************
        
        The application provides a comprehensive dashboard with multiple views:
        
        a) Dashboard Overview:
           - Summary statistics including unique sample counts
           - Status distribution table
           - Key metrics for all scenarios
           - Both average and median statistics for robust analysis
        
        b) Charts & Analysis:
           - Scenario distribution pie chart
           - TAT comparison bar charts (average vs median)
           - Visual representation of data patterns
           - Print capabilities for all charts
        
        c) 3D Parameter Analysis:
           - Three-dimensional visualization of parameter-specific TAT data
           - Interactive parameter selection
           - Comparison of average and median values per parameter
        
        d) Filtering and Exclusion:
           - Filter by Sample ID, Component, Scenario, and Parameter
           - Exclude specific components or parameters from analysis
           - Clear visual indication of excluded items
           - Real-time updates to all visualizations
        
        6. Export and Reporting
        **********************
        
        a) PDF Export:
           - Generate comprehensive PDF reports
           - Customizable title, date, and department
           - Includes summary statistics and parameter analysis
           - Professional formatting for management reports
        
        b) CSV Export:
           - Export filtered results to CSV format
           - Preserves all calculated metrics
           - Suitable for further analysis in other tools
        
        c) Print Functionality:
           - Print dashboard overviews
           - Print individual charts
           - Print full reports
           - Customizable print settings
        
        d) Specialized Exports:
           - Export incomplete data for further investigation
           - Export invalid records for correction
           - Export correction details for audit purposes
        
        7. Advanced Features
        *******************
        
        a) Custom Columns:
           - Add custom columns to the analysis table
           - Editable cells for additional data
           - Preserved during data updates
        
        b) Parameter Management:
           - Add custom parameters to statistics
           - Manual entry of parameter data
           - Integration with calculated statistics
        
        c) Data Accumulation:
           - Load data from multiple files over time
           - Automatic deduplication based on sample IDs
           - Preserves all historical data
           - Status tracking shows total records and unique samples
        
        d) Statistical Analysis:
           - Both mean and median calculations
           - Min/Max values for parameters
           - Scenario-based statistics
           - Automation efficiency metrics
        
        e) Help and Documentation:
           - Comprehensive help system
           - Detailed explanation of all calculations
           - Scenario analysis tools
           - Debug information for troubleshooting
        
        Understanding Summary Statistics:
        *********************************
        
        Important Notes:
        - Only samples with valid timing relationships contribute to "normal" TAT statistics
        - Special cases are handled appropriately without skewing the results
        - All statistics are calculated based on UNIQUE sample IDs to avoid duplication
        - Incomplete samples are excluded from most statistical calculations
        
        Median vs. Average (Mean):
        
        - Average (Mean): The mathematical average of all values (sum divided by count)
          - Example: For values 5, 7, 8, 10, 120 minutes: 
            Average = (5+7+8+10+120)/5 = 30 minutes
        
        - Median: The middle value when all values are sorted in numerical order
          - Example: For values 5, 7, 8, 10, 120 minutes (sorted):
            Median = 8 minutes (the middle value)
        
        Why Median is Important in TAT Analysis:
        ****************************************
        
        1. Robust to Outliers: Unlike the average, the median isn't skewed by extremely 
           long processing times that might occur due to unusual circumstances.
        
        2. Better Representation: For most laboratory processes, the median gives a more 
           realistic picture of "typical" performance than the average.
        
        3. Performance Benchmarking: The median TAT represents what most samples achieve, 
           which is more useful for setting expectations and performance targets.
        
        When reviewing your laboratory's performance, comparing both the average and median 
        can help you understand whether your process is generally consistent (similar average 
        and median) or if there are outliers affecting the overall performance (significantly 
        different average and median).
        
        Scenario Decision Tree:
        **********************
        
        The following logic is used to determine the scenario and TAT calculations:
        
        1. Does the sample have both "Tube Created" and "Host Upload" events?
           - If NO: Incomplete scenario - skip sample
           - If YES: Continue
        
        2. Is "Arrived At Input" time before "Tube Created" time?
           - If YES: LIS Down scenario
             - No TAT calculations
             - Status = "Invalid"
             - If "Arrived At Input" is also before "Host Upload": mark as automation processed
           - If NO: Continue
        
        3. Is "Arrived At Input" time between "Tube Created" and "Host Upload"?
           - If YES: Normal scenario
             - Full TAT calculation using Arrived At Input time
             - Status = "Valid" or "Review - Delayed Sample" (if preprocessing > 60 min)
             - Mark as automation processed
           - If NO: Continue
        
        4. Is "Instrument Download" time available?
           - If YES: Direct Analysis scenario
             - Calculate TAT using Instrument Download time
             - If "Arrived At Input" is after "Host Upload": 
                 Status = "ECSD Storage" or "ECSD Storage - Delayed Sample"
                 Mark as ECSD direct stored
             - Else: Status = "Valid" or "Review - Delayed Sample"
           - If NO: 
             - If "Arrived At Input" is after "Host Upload":
                 Status = "ECSD Storage - No Instrument Download"
                 Mark as ECSD direct stored
             - Else: Status = "No Instrument Download"
        
        5. If "Loaded Into Storage" event exists: mark as ECSD total loaded
        
        This ensures accurate representation of actual laboratory workflow timing and proper
        classification of all samples into appropriate scenarios.
        """
        
        text_edit = QTextEdit()
        text_edit.setPlainText(help_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Add close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)