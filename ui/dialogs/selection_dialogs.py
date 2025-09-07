"""
Selection dialog classes for filtering and choosing options.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QDialogButtonBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from ui.components.styled_button import StyledButton
from .base_dialogs import BaseDialog


class MultiSelectDialog(BaseDialog):
    """Dialog for selecting multiple items to exclude"""
    def __init__(self, title, items, parent=None):
        self.items = items
        super().__init__(title, parent, 400, 500)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_edit)
        
        # List widget for selection
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.list_widget)
        
        # Add all items
        self.all_items = self.items
        for item in self.items:
            self.list_widget.addItem(item)
        
        # Buttons
        button_layout = QHBoxLayout()
        select_all_btn = StyledButton("Select All", None, self)
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        clear_btn = StyledButton("Clear", None, self)
        clear_btn.clicked.connect(self.clear_selection)
        button_layout.addWidget(clear_btn)
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def filter_items(self):
        """Filter items based on search text"""
        search_text = self.search_edit.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())
    
    def select_all(self):
        """Select all visible items"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                item.setSelected(True)
    
    def clear_selection(self):
        """Clear all selections"""
        self.list_widget.clearSelection()
    
    def get_selected_items(self):
        """Get list of selected items"""
        return [item.text() for item in self.list_widget.selectedItems()]


class StatisticsSelectionDialog(BaseDialog):
    """Dialog for selecting which statistics to include in reports"""
    def __init__(self, parent=None):
        super().__init__("Select Statistics to Include", parent, 400, 500)
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Explanation
        explanation = QLabel("Select which statistics to include in the report:")
        layout.addWidget(explanation)
        
        # List widget for selection
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.list_widget)
        
        # Add all statistics options
        statistics = [
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
        
        for stat in statistics:
            item = QListWidgetItem(stat)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)  # All checked by default
            self.list_widget.addItem(item)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = StyledButton("Select All", None, self)
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        clear_btn = StyledButton("Clear All", None, self)
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def select_all(self):
        """Select all statistics"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def clear_all(self):
        """Clear all selections"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def get_selected_statistics(self):
        """Get list of selected statistics"""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected