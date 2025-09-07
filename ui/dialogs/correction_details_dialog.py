"""
Dialog for displaying correction details in a table format.
"""
import pandas as pd
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QHeaderView, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from .base_dialogs import BaseDialog


class CorrectionDetailsDialog(BaseDialog):
    """Dialog to display detailed correction information in a table"""
    def __init__(self, correction_data, parent=None):
        self.correction_data = correction_data
        super().__init__("Correction Details", parent, 1000, 700)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Create table for correction details
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Original Index', 'Sample ID', 'Component', 'Event', 
            'Original DateTime', 'Corrected DateTime', 'Status'
        ])
        
        # Populate table
        self.table.setRowCount(len(self.correction_data))
        for row, data in enumerate(self.correction_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(data['Original_Index'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(data['Sample ID'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(data['Component'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(data['Event'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(data['Original_DateTime_String'])))
            
            corrected_dt = data['Corrected_DateTime']
            if pd.isna(corrected_dt):
                self.table.setItem(row, 5, QTableWidgetItem("Invalid"))
                status_item = QTableWidgetItem("Failed")
                status_item.setBackground(QBrush(QColor(255, 200, 200)))  # Light red
            else:
                self.table.setItem(row, 5, QTableWidgetItem(corrected_dt.strftime('%Y-%m-%d %H:%M:%S')))
                status_item = QTableWidgetItem("Success")
                status_item.setBackground(QBrush(QColor(200, 255, 200)))  # Light green
            
            self.table.setItem(row, 6, status_item)
        
        # Set table properties
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        
        layout.addWidget(self.table)
        
        # Add summary label
        successful = len([d for d in self.correction_data if not pd.isna(d['Corrected_DateTime'])])
        failed = len([d for d in self.correction_data if pd.isna(d['Corrected_DateTime'])])
        summary_text = f"""
Summary:
- Total corrections: {len(self.correction_data)}
- Successful: {successful}
- Failed: {failed}
        """
        summary_label = QLabel(summary_text)
        layout.addWidget(summary_label)
        
        # Add close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)