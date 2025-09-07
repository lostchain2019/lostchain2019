#!/usr/bin/env python3
"""
Laboratory TAT Analysis Application
Main entry point for the application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import TimeCalculator


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Create and show the main window
    calculator = TimeCalculator()
    calculator.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()