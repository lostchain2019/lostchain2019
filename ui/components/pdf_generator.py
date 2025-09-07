"""
PDF generation component for creating reports.
"""
from datetime import datetime
from config.dependencies import PDF_AVAILABLE, FPDF


class PDFGenerator:
    """Class to generate PDF reports"""
    def __init__(self, selected_statistics=None):
        if not PDF_AVAILABLE:
            raise ImportError("FPDF library not available")
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.selected_statistics = selected_statistics or []
        
    def add_title_page(self, title, date, department):
        """Add title page to PDF"""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        
        # Department
        self.pdf.set_font('Arial', '', 14)
        self.pdf.cell(0, 10, department, ln=True, align='C')
        
        # Date
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, date, ln=True, align='C')
        
        # Generation time
        self.pdf.set_font('Arial', 'I', 10)
        self.pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        
        # Add spacing
        self.pdf.ln(20)
    
    def add_summary_statistics(self, summary_stats):
        """Add summary statistics to PDF"""
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, "Summary Statistics", ln=True)
        self.pdf.ln(10)
        
        self.pdf.set_font('Arial', '', 12)
        # Only add selected statistics
        for metric, value in summary_stats.items():
            if metric in self.selected_statistics:
                self.pdf.cell(0, 8, f"{metric}: {value}", ln=True)
        
        self.pdf.ln(10)
    
    def add_parameter_statistics(self, parameter_stats):
        """Add parameter statistics to PDF"""
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, "Parameter TAT Statistics", ln=True)
        self.pdf.ln(10)
        
        # Table header
        self.pdf.set_font('Arial', 'B', 10)
        col_widths = [40, 20, 30, 30, 30, 30]
        headers = ['Parameter', 'Count', 'Avg TAT', 'Median TAT', 'Min TAT', 'Max TAT']
        for i, header in enumerate(headers):
            self.pdf.cell(col_widths[i], 8, header, border=1, align='C')
        self.pdf.ln()
        
        # Table data
        self.pdf.set_font('Arial', '', 9)
        for stats in parameter_stats:
            self.pdf.cell(col_widths[0], 8, str(stats['Parameter'])[:25], border=1)
            self.pdf.cell(col_widths[1], 8, str(stats['Count']), border=1, align='C')
            self.pdf.cell(col_widths[2], 8, f"{stats['Avg TAT (min)']:.2f}", border=1, align='C')
            self.pdf.cell(col_widths[3], 8, f"{stats['Median TAT (min)']:.2f}", border=1, align='C')
            self.pdf.cell(col_widths[4], 8, f"{stats['Min TAT (min)']:.2f}", border=1, align='C')
            self.pdf.cell(col_widths[5], 8, f"{stats['Max TAT (min)']:.2f}", border=1, align='C')
            self.pdf.ln()
        
        self.pdf.ln(10)
    
    def save(self, filename):
        """Save PDF to file"""
        self.pdf.output(filename)