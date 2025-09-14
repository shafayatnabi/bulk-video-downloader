#!/usr/bin/env python3
"""
Main entry point for the Bulk Video Downloader application
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Bulk Video Downloader")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
