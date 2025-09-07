"""
Dashboard overview tab with summary statistics and status distribution.
"""
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QBrush, QColor
from ui.components.styled_button import StyledButton
from ui.dialogs.print_dialog import ChartPrintDialog


class DashboardOverviewTab(QWidget):
    """Dashboard overview tab showing summary statistics and status distribution"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Laboratory TAT Dashboard Overview")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Print button for overview
        print_layout = QHBoxLayout()
        print_layout.addStretch()
        
        self.print_overview_btn = StyledButton("Print Overview", None, self)
        self.print_overview_btn.clicked.connect(self.print_overview)
        print_layout.addWidget(self.print_overview_btn)
        
        layout.addLayout(print_layout)
        
        # Summary Statistics Section
        self.summary_group = QGroupBox("Summary Statistics")
        summary_layout = QVBoxLayout()
        self.summary_group.setLayout(summary_layout)
        
        # Create a grid layout for summary statistics
        self.summary_grid = QGridLayout()
        summary_layout.addLayout(self.summary_grid)
        
        # Initialize summary labels
        self.summary_labels = {}
        metrics = [
            "Total Samples",
            "Complete Samples",
            "Incomplete Samples",
            "LIS Down Cases",
            "Direct Analysis Cases",
            "Automation Processed Samples",
            "Avg Preprocessing Time",
            "Avg Analytical TAT",
            "Avg Total TAT",
            "Median Preprocessing Time",
            "Median Analytical TAT",
            "Median Total TAT"
        ]
        
        for i, metric in enumerate(metrics):
            # Create metric label
            metric_label = QLabel(metric + ":")
            metric_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.summary_grid.addWidget(metric_label, i // 2, (i % 2) * 2)
            
            # Create value label
            value_label = QLabel("N/A")
            value_label.setFont(QFont("Arial", 10))
            value_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc; border-radius: 4px; }")
            self.summary_grid.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
            self.summary_labels[metric] = value_label
        
        layout.addWidget(self.summary_group)
        
        # Status Distribution Section
        self.status_group = QGroupBox("Status Distribution")
        status_layout = QVBoxLayout()
        self.status_group.setLayout(status_layout)
        
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(['Status', 'Count', 'Percentage'])
        
        # Set table properties
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.status_table.horizontalHeader().setStretchLastSection(False)
        
        status_layout.addWidget(self.status_table)
        layout.addWidget(self.status_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def update_dashboard(self, sample_results, parameter_stats, processing_thread):
        """Update the dashboard overview with new data"""
        # Update summary statistics
        self.update_summary_statistics(sample_results, processing_thread)
        
        # Update status distribution
        self.update_status_distribution(sample_results)
    
    def update_summary_statistics(self, sample_results, processing_thread):
        """Update summary statistics display"""
        if not sample_results:
            return
        
        # Convert to DataFrame for easier calculations
        sample_df = pd.DataFrame(sample_results)
        
        # Calculate total sample counts
        total_samples = len(sample_results)
        complete_samples = [r for r in sample_results if r['Scenario'] != "Incomplete"]
        incomplete_samples = [r for r in sample_results if r['Scenario'] == "Incomplete"]
        complete_count = len(complete_samples)
        incomplete_count = len(incomplete_samples)
        
        # Update total sample counts
        self.summary_labels["Total Samples"].setText(str(total_samples))
        self.summary_labels["Complete Samples"].setText(str(complete_count))
        self.summary_labels["Incomplete Samples"].setText(str(incomplete_count))
        
        # Filter out incomplete samples for other statistics
        complete_df = pd.DataFrame(complete_samples)
        
        # Scenario counts - exclude incomplete
        scenario_counts = {"Normal": 0, "LIS Down": 0, "Direct Analysis": 0}
        for scenario in scenario_counts.keys():
            scenario_counts[scenario] = len([r for r in complete_samples if r['Scenario'] == scenario])
        
        lis_down_count = scenario_counts.get("LIS Down", 0)
        direct_analysis_count = scenario_counts.get("Direct Analysis", 0)
        
        self.summary_labels["LIS Down Cases"].setText(str(lis_down_count))
        self.summary_labels["Direct Analysis Cases"].setText(str(direct_analysis_count))
        
        # Automation processed samples
        automation_count = len(processing_thread.automation_processed_samples) if hasattr(processing_thread, 'automation_processed_samples') else 0
        self.summary_labels["Automation Processed Samples"].setText(str(automation_count))
        
        # Calculate statistics for valid cases (exclude LIS Down)
        valid_df = complete_df[complete_df['Scenario'].isin(['Normal', 'Direct Analysis'])]
        
        if not valid_df.empty:
            # Average times
            avg_prep = valid_df['Preprocessing Time (min)'].mean()
            avg_analytical = valid_df['Analytical TAT (min)'].mean()
            avg_total = valid_df['Total TAT (min)'].mean()
            
            self.summary_labels["Avg Preprocessing Time"].setText(f"{avg_prep:.2f} min" if not pd.isna(avg_prep) else "N/A")
            self.summary_labels["Avg Analytical TAT"].setText(f"{avg_analytical:.2f} min" if not pd.isna(avg_analytical) else "N/A")
            self.summary_labels["Avg Total TAT"].setText(f"{avg_total:.2f} min" if not pd.isna(avg_total) else "N/A")
            
            # Median times
            median_prep = valid_df['Preprocessing Time (min)'].median()
            median_analytical = valid_df['Analytical TAT (min)'].median()
            median_total = valid_df['Total TAT (min)'].median()
            
            self.summary_labels["Median Preprocessing Time"].setText(f"{median_prep:.2f} min" if not pd.isna(median_prep) else "N/A")
            self.summary_labels["Median Analytical TAT"].setText(f"{median_analytical:.2f} min" if not pd.isna(median_analytical) else "N/A")
            self.summary_labels["Median Total TAT"].setText(f"{median_total:.2f} min" if not pd.isna(median_total) else "N/A")
        else:
            # No valid cases
            for metric in ["Avg Preprocessing Time", "Avg Analytical TAT", "Avg Total TAT",
                          "Median Preprocessing Time", "Median Analytical TAT", "Median Total TAT"]:
                self.summary_labels[metric].setText("N/A")
    
    def update_status_distribution(self, sample_results):
        """Update status distribution table"""
        if not sample_results:
            self.status_table.setRowCount(0)
            return
        
        # Count statuses
        status_counts = {}
        for result in sample_results:
            status = result['Status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate total for percentages
        total = sum(status_counts.values())
        
        # Update table
        self.status_table.setRowCount(len(status_counts))
        
        for row, (status, count) in enumerate(status_counts.items()):
            # Status
            status_item = QTableWidgetItem(str(status))
            if status == "Invalid":
                status_item.setBackground(QBrush(QColor(255, 200, 200)))  # Light red
            elif "Delayed Sample" in str(status):
                status_item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
            elif "ECSD Storage" in str(status):
                status_item.setBackground(QBrush(QColor(200, 200, 255)))  # Light blue
            self.status_table.setItem(row, 0, status_item)
            
            # Count
            self.status_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # Percentage
            percentage = (count / total * 100) if total > 0 else 0
            self.status_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
        
        # Resize columns to content
        self.status_table.resizeColumnsToContents()
    
    def print_overview(self):
        """Print the dashboard overview"""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt6.QtGui import QPainter, QPixmap, QPageLayout
            from PyQt6.QtCore import QRect, Qt
            from PyQt6.QtWidgets import QMessageBox, QDialog
            
            # Create printer
            printer = QPrinter()
            printer.setPageSize(printer.PageSize.A4)
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            
            # Show print dialog
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Create a pixmap of the widget
                pixmap = QPixmap(self.size())
                self.render(pixmap)
                
                # Print the pixmap
                painter = QPainter(printer)
                
                # Calculate scaling to fit page
                page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
                pixmap_rect = pixmap.rect()
                
                # Scale pixmap to fit page while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(page_rect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # Center the pixmap on the page
                x = int((page_rect.width() - scaled_pixmap.width()) // 2)
                y = int((page_rect.height() - scaled_pixmap.height()) // 2)
                
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                QMessageBox.information(self, "Success", "Dashboard overview printed successfully!")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to print dashboard overview: {str(e)}")