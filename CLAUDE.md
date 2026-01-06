# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bank to Budget Converter - A Python/Tkinter desktop application that converts Russian bank export files (CSV/XLSX) into a format suitable for Google Sheets budget tracking.

## Running the Application

```bash
python run_converter.py
```

For XLSX support, install openpyxl first:
```bash
pip install openpyxl
```

## Architecture

**Data Flow:**
1. `BankFileReader` parses bank export → `BankTransaction` objects
2. `BankConverter` transforms using config mappings → `BudgetTransaction` objects
3. Unknown categories/vendors trigger `MappingDialog` for user resolution (saved to config)
4. `BudgetWriter` outputs separated income/expense sections

**Key Modules:**
- `core/models.py` - Dataclasses: `BankTransaction`, `BudgetTransaction`, `UnknownMapping`, `TransactionType` enum
- `core/reader.py` - Multi-encoding CSV/XLSX parsing, `parse_amount()` handles Russian comma decimals
- `core/converter.py` - Mapping logic: vendor overrides take priority over category mappings
- `core/writer.py` - CSV output with `to_clipboard_text()` for direct Google Sheets paste
- `config/manager.py` - JSON config with category→tag and vendor→(tag, name) mappings

**Configuration:**
- Stored in `bank_converter/mappings.json` (auto-created on first run)
- Contains: owner, output_tags, category_mappings, vendor_overrides, skip_descriptions
- User-defined mappings persist across sessions

## Important Conventions

- All bank column names and UI labels are in Russian
- Amounts use Russian format (comma as decimal separator: "4363,00")
- Dates use DD.MM.YYYY format
- Internal transfers ("Между своими счетами") are skipped by default
- Positive amounts = income, negative = expenses (unless category is in income_categories)

## Sample Data

`examples/` contains sample bank export files (CSV and XLSX) for testing.
