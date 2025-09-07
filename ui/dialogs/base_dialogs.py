"""
Base dialog classes and common dialog utilities.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit,
    QDialogButtonBox, QFormLayout, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime


class BaseDialog(QDialog):
    """Base dialog with common functionality"""
    def __init__(self, title, parent=None, min_width=400, min_height=200):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)
        self.setupUI()
    
    def setupUI(self):
        """Override in subclasses to setup UI"""
        pass


class TitleInputDialog(BaseDialog):
    """Dialog for entering report title"""
    def __init__(self, parent=None):
        super().__init__("Enter Report Title", parent, 400, 200)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Title input
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter report title...")
        layout.addWidget(QLabel("Report Title:"))
        layout.addWidget(self.title_edit)
        
        # Date input
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.now().strftime("%Y-%m-%d"))
        layout.addWidget(QLabel("Report Date:"))
        layout.addWidget(self.date_edit)
        
        # Department input
        self.dept_edit = QLineEdit()
        self.dept_edit.setPlaceholderText("Enter department name...")
        layout.addWidget(QLabel("Department:"))
        layout.addWidget(self.dept_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_values(self):
        return {
            'title': self.title_edit.text(),
            'date': self.date_edit.text(),
            'department': self.dept_edit.text()
        }


class AdjustTimeDialog(BaseDialog):
    """Dialog for adjusting Arrived At Input time"""
    def __init__(self, parent=None):
        super().__init__("Adjust Arrived At Input Time", parent, 400, 200)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Explanation label
        explanation = QLabel(
            "Adjust the 'Arrived At Input' time for all samples by adding or subtracting hours.\n"
            "This will recalculate all TAT metrics and statistics."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
        # Hours adjustment
        hours_layout = QHBoxLayout()
        hours_layout.addWidget(QLabel("Adjustment (hours):"))
        
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(-1000, 1000)
        self.hours_spin.setValue(0)
        self.hours_spin.setSingleStep(0.5)
        self.hours_spin.setDecimals(1)
        hours_layout.addWidget(self.hours_spin)
        
        layout.addLayout(hours_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_adjustment(self):
        return self.hours_spin.value()


class AddParameterDialog(BaseDialog):
    """Dialog for adding a new parameter to statistics"""
    def __init__(self, parent=None):
        super().__init__("Add Parameter", parent, 400, 300)
        
    def setupUI(self):
        layout = QFormLayout()
        
        # Parameter name
        self.param_name_edit = QLineEdit()
        self.param_name_edit.setPlaceholderText("Enter parameter name...")
        layout.addRow("Parameter Name:", self.param_name_edit)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(0)
        self.count_spin.setMaximum(1000000)
        self.count_spin.setValue(1)
        layout.addRow("Count:", self.count_spin)
        
        # Average TAT
        self.avg_spin = QDoubleSpinBox()
        self.avg_spin.setMinimum(0)
        self.avg_spin.setMaximum(1000000)
        self.avg_spin.setDecimals(2)
        self.avg_spin.setValue(0.0)
        layout.addRow("Avg TAT (min):", self.avg_spin)
        
        # Median TAT
        self.median_spin = QDoubleSpinBox()
        self.median_spin.setMinimum(0)
        self.median_spin.setMaximum(1000000)
        self.median_spin.setDecimals(2)
        self.median_spin.setValue(0.0)
        layout.addRow("Median TAT (min):", self.median_spin)
        
        # Min TAT
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setMinimum(0)
        self.min_spin.setMaximum(1000000)
        self.min_spin.setDecimals(2)
        self.min_spin.setValue(0.0)
        layout.addRow("Min TAT (min):", self.min_spin)
        
        # Max TAT
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setMinimum(0)
        self.max_spin.setMaximum(1000000)
        self.max_spin.setDecimals(2)
        self.max_spin.setValue(0.0)
        layout.addRow("Max TAT (min):", self.max_spin)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_values(self):
        return {
            'Parameter': self.param_name_edit.text(),
            'Count': self.count_spin.value(),
            'Avg TAT (min)': self.avg_spin.value(),
            'Median TAT (min)': self.median_spin.value(),
            'Min TAT (min)': self.min_spin.value(),
            'Max TAT (min)': self.max_spin.value(),
            'manual': True  # Mark as manually added
        }


class DebugDialog(BaseDialog):
    """Dialog for showing debug information"""
    def __init__(self, text, parent=None):
        super().__init__("Debug Information", parent, 800, 600)
        self.debug_text = text
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setPlainText(self.debug_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Add close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


class ScenarioAnalysisDialog(BaseDialog):
    """Dialog for showing scenario analysis"""
    def __init__(self, analysis_text, parent=None):
        super().__init__("Scenario Analysis", parent, 800, 600)
        self.analysis_text = analysis_text
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setPlainText(self.analysis_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Add close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)