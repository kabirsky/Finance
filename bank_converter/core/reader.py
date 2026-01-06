"""File readers for bank export data."""

import csv
from pathlib import Path
from typing import List, Optional

from .models import BankTransaction


class BankFileReader:
    """Reads bank export files (CSV or XLSX)."""

    EXPECTED_COLUMNS = [
        "Дата операции", "Дата платежа", "Номер карты", "Статус",
        "Сумма операции", "Валюта операции", "Сумма платежа",
        "Валюта платежа", "Кэшбэк", "Категория", "MCC", "Описание"
    ]

    def read(self, file_path: str) -> List[BankTransaction]:
        """Read file and return list of transactions.

        Args:
            file_path: Path to bank export file (CSV or XLSX).

        Returns:
            List of BankTransaction objects.

        Raises:
            ValueError: If file format is not supported.
        """
        path = Path(file_path)
        if path.suffix.lower() == '.xlsx':
            return self._read_xlsx(path)
        elif path.suffix.lower() == '.csv':
            return self._read_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def _read_csv(self, path: Path) -> List[BankTransaction]:
        """Read semicolon-separated CSV with UTF-8 encoding."""
        transactions = []

        # Try different encodings
        for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f, delimiter=';', quotechar='"')
                    for row in reader:
                        tx = self._parse_row(row)
                        if tx:
                            transactions.append(tx)
                return transactions
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == 'windows-1251':
                    raise e
                continue

        raise ValueError("Could not read file with any supported encoding")

    def _read_xlsx(self, path: Path) -> List[BankTransaction]:
        """Read XLSX file using openpyxl."""
        try:
            import openpyxl
        except ImportError:
            raise ImportError(
                "openpyxl is required for XLSX support. "
                "Install it with: pip install openpyxl"
            )

        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        transactions = []

        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return transactions

        # First row is headers
        headers = [str(cell) if cell else "" for cell in rows[0]]

        for row in rows[1:]:
            if not row or all(cell is None for cell in row):
                continue
            row_dict = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else None
                row_dict[header] = str(value) if value is not None else ""
            tx = self._parse_row(row_dict)
            if tx:
                transactions.append(tx)

        workbook.close()
        return transactions

    def _parse_row(self, row: dict) -> Optional[BankTransaction]:
        """Parse row dict into BankTransaction."""
        # Skip empty rows
        if not row or not row.get("Дата операции"):
            return None

        return BankTransaction(
            operation_date=self._clean_str(row.get("Дата операции", "")),
            payment_date=self._clean_str(row.get("Дата платежа", "")),
            card_number=self._clean_str(row.get("Номер карты", "")),
            status=self._clean_str(row.get("Статус", "")),
            amount=self._clean_str(row.get("Сумма операции", "")),
            currency=self._clean_str(row.get("Валюта операции", "")),
            category=self._clean_str(row.get("Категория", "")),
            mcc=self._clean_str(row.get("MCC", "")),
            description=self._clean_str(row.get("Описание", ""))
        )

    def _clean_str(self, value: str) -> str:
        """Clean string value - remove quotes, strip whitespace."""
        if not value:
            return ""
        return str(value).strip().strip('"')


def parse_amount(amount_str: str) -> float:
    """Parse Russian-formatted amount string to float.

    Args:
        amount_str: Amount string like "-4363,00" or "142000.00"

    Returns:
        Float value of the amount.
    """
    if not amount_str:
        return 0.0

    # Remove quotes, replace comma with dot, remove spaces
    cleaned = str(amount_str).strip('"').replace(',', '.').replace(' ', '')
    cleaned = cleaned.replace('\xa0', '')  # Non-breaking space

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_date(date_str: str) -> str:
    """Convert 'DD.MM.YYYY HH:MM:SS' to 'DD.MM.YYYY'.

    Args:
        date_str: Date string with optional time component.

    Returns:
        Date string in DD.MM.YYYY format.
    """
    if not date_str:
        return ""

    date_str = str(date_str).strip().strip('"')

    # Handle datetime format
    if ' ' in date_str:
        date_str = date_str.split(' ')[0]

    return date_str
