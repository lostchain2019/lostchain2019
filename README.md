# Laboratory TAT Analysis Application

A comprehensive PyQt6-based application for analyzing laboratory sample processing times and calculating Turnaround Time (TAT) metrics.

## Features

- **Multi-file CSV loading** with automatic format detection
- **Comprehensive TAT calculations** with scenario-based analysis
- **Interactive dashboard** with visualizations and charts
- **Advanced filtering and exclusion** options
- **Export capabilities** (PDF, CSV) with customizable reports
- **Raw data editing** and correction capabilities
- **3D parameter analysis** and visualization
- **Print functionality** for reports and charts

## Project Structure

```
laboratory-tat-analysis/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # Project documentation
├── config/                         # Configuration and constants
│   ├── __init__.py
│   ├── constants.py               # Application constants
│   └── dependencies.py            # Optional library management
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── datetime_utils.py          # Datetime parsing utilities
│   ├── file_utils.py              # File handling utilities
│   └── parameter_utils.py         # Parameter extraction utilities
├── data_processing/               # Data processing logic
│   ├── __init__.py
│   ├── csv_loader.py              # CSV loading and parsing
│   └── data_processor.py          # Main TAT calculation logic
└── ui/                           # User interface components
    ├── __init__.py
    ├── main_window.py            # Main application window (to be created)
    ├── components/               # Reusable UI components
    │   ├── __init__.py
    │   ├── styled_button.py      # Custom styled buttons
    │   ├── chart_components.py   # Chart visualization components
    │   └── pdf_generator.py      # PDF report generation
    ├── dialogs/                  # Dialog windows
    │   ├── __init__.py
    │   ├── base_dialogs.py       # Base dialog classes
    │   ├── selection_dialogs.py  # Selection and filtering dialogs
    │   ├── help_dialog.py        # Help documentation dialog
    │   └── correction_details_dialog.py  # Correction details display
    └── dashboard/                # Dashboard components
        ├── __init__.py
        └── overview_tab.py       # Dashboard overview tab
```

## Installation

1. **Clone or download** the project files to your local machine.

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional dependencies** (install as needed):
   - For PDF export: `pip install fpdf2`
   - For advanced datetime parsing: `pip install python-dateutil`
   - For encoding detection: `pip install chardet`

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Load CSV data:**
   - Click "Load CSV File(s)" to select one or more CSV files
   - The application automatically detects file format and encoding
   - Data is accumulated from multiple files

3. **Analyze results:**
   - View summary statistics in the Dashboard tab
   - Examine detailed results in the Time Analysis tab
   - Use filtering options to focus on specific samples or parameters

4. **Export results:**
   - Generate PDF reports with customizable statistics
   - Export filtered data to CSV format
   - Print charts and dashboard overviews

## TAT Calculation Methodology

The application calculates three key TAT metrics:

### 1. Preprocessing Time
- Time between "Tube Created" and "Arrived At Input"
- Formula: `Preprocessing Time = Arrived At Input Time - Tube Created Time`

### 2. Analytical TAT
- Time between "Arrived At Input" and "Host Upload"
- Formula: `Analytical TAT = Host Upload Time - Arrived At Input Time`

### 3. Total TAT
- Time between "Tube Created" and "Host Upload"
- Formula: `Total TAT = Host Upload Time - Tube Created Time`

## Scenario Classification

The application automatically classifies samples into different scenarios:

- **Normal**: Standard workflow with all timing events in correct sequence
- **LIS Down**: System timing issues where "Arrived At Input" occurs before "Tube Created"
- **Direct Analysis**: Alternative workflow using "Instrument Download" timing
- **Incomplete**: Missing critical timing events

## Data Management

- **Multi-file support**: Load and accumulate data from multiple CSV files
- **Format detection**: Automatic detection of delimiters, encoding, and column structure
- **Data validation**: Identification and handling of invalid datetime records
- **Correction support**: Load corrected data to update specific datetime values

## Advanced Features

- **Custom columns**: Add editable custom columns to analysis tables
- **Parameter management**: Add custom parameters to statistics
- **Filtering and exclusion**: Exclude specific components or parameters from analysis
- **3D visualization**: Three-dimensional parameter analysis charts
- **Time adjustment**: Bulk adjustment of "Arrived At Input" times

## System Requirements

- Python 3.8 or higher
- PyQt6 6.4.0 or higher
- pandas 1.5.0 or higher
- numpy 1.21.0 or higher

## Optional Requirements

- matplotlib 3.5.0+ (for charts)
- fpdf2 2.7.0+ (for PDF export)
- python-dateutil 2.8.0+ (for advanced datetime parsing)
- chardet 5.0.0+ (for encoding detection)

## Troubleshooting

### PDF Export Issues
If PDF export is not available:
1. Install FPDF library: `pip install fpdf2`
2. Restart the application
3. Use "Tools > Install PDF Library" for detailed installation help

### CSV Loading Issues
If CSV files fail to load:
1. Check file encoding (UTF-8, Latin-1 supported)
2. Verify delimiter consistency (semicolon, comma supported)
3. Ensure required columns are present (Sample ID, Event, DateTime)

### Performance Issues
For large datasets:
1. Load files individually rather than all at once
2. Use filtering to focus on specific time ranges
3. Consider splitting very large files before loading

## Support

For help with TAT calculations and scenarios, use the built-in help system:
- Menu: Help > TAT Calculation Help
- Comprehensive documentation of all calculation methods
- Scenario decision tree explanation
- Statistical analysis guidance

## License

This project is provided as-is for laboratory data analysis purposes.