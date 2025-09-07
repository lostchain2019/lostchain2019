"""
Dependency management for optional libraries.
"""

# Try to import dateutil for advanced datetime parsing
try:
    from dateutil.parser import parse as dateutil_parse
    DATEUTIL_AVAILABLE = True
    print("dateutil library detected successfully")
except ImportError:
    DATEUTIL_AVAILABLE = False
    print("dateutil library not available. Using built-in datetime parsing only.")

# PDF generation imports - updated to support both fpdf and fpdf2
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
    print("FPDF library detected successfully")
except ImportError:
    try:
        from fpdf2 import FPDF  # Try fpdf2 import
        PDF_AVAILABLE = True
        print("FPDF2 library detected successfully")
    except ImportError:
        PDF_AVAILABLE = False
        print("FPDF library not available. PDF export will be disabled.")

# Matplotlib for charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Chart features will be disabled.")

# Character encoding detection
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    print("chardet not available. Using basic encoding detection.")