#!/usr/bin/env python3
"""Bank to Budget Converter - Entry Point.

A tool for converting bank export data to Google Sheets budget format.

Usage:
    python main.py           # Launch GUI
    python -m bank_converter # Alternative launch

Requirements:
    - Python 3.8+
    - openpyxl (for XLSX support): pip install openpyxl
"""

import sys


def main():
    """Main entry point."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

    # Import and run the app
    from bank_converter.gui.app import BankConverterApp

    app = BankConverterApp()
    app.run()


if __name__ == "__main__":
    main()
