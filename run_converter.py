#!/usr/bin/env python3
"""Run the Bank to Budget Converter application."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bank_converter.gui.app import BankConverterApp

if __name__ == "__main__":
    app = BankConverterApp()
    app.run()
