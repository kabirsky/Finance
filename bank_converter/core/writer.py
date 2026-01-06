"""Output writer for budget data."""

import csv
from typing import List

from .models import BudgetTransaction, TransactionType


class BudgetWriter:
    """Writes converted data to CSV for Google Sheets."""

    def write(self, transactions: List[BudgetTransaction], output_path: str):
        """Write transactions to CSV file.

        Args:
            transactions: List of BudgetTransaction objects.
            output_path: Path to output CSV file.
        """
        income = [tx for tx in transactions
                  if tx.transaction_type == TransactionType.INCOME]
        expenses = [tx for tx in transactions
                    if tx.transaction_type == TransactionType.EXPENSE]

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Income section
            self._write_section(writer, "Доход", income)

            # Empty rows between sections
            writer.writerow([])
            writer.writerow([])

            # Expense section
            self._write_section(writer, "Расход", expenses)

    def _write_section(
        self, writer: csv.writer, title: str, transactions: List[BudgetTransaction]
    ):
        """Write a section (income or expense).

        Args:
            writer: CSV writer object.
            title: Section title ("Доход" or "Расход").
            transactions: List of transactions for this section.
        """
        writer.writerow([title])
        writer.writerow(["Чей", "Дата", "Сумма", "Назначение", "Тег", "Комментарий"])

        # Sort by date
        sorted_transactions = sorted(
            transactions,
            key=lambda x: self._parse_date_for_sort(x.date)
        )

        for tx in sorted_transactions:
            writer.writerow([
                tx.owner,
                tx.date,
                self._format_amount(tx.amount),
                tx.purpose,
                tx.tag,
                tx.comment
            ])

    def _format_amount(self, amount: float) -> str:
        """Format amount for output.

        Uses integer format for whole numbers, otherwise 2 decimal places.

        Args:
            amount: Amount to format.

        Returns:
            Formatted amount string.
        """
        if amount == int(amount):
            return str(int(amount))
        # Format with 2 decimals, using comma as separator (Russian format)
        return f"{amount:.2f}".replace('.', ',')

    def _parse_date_for_sort(self, date_str: str) -> tuple:
        """Parse date string for sorting.

        Args:
            date_str: Date in DD.MM.YYYY format.

        Returns:
            Tuple (year, month, day) for sorting.
        """
        if not date_str:
            return (0, 0, 0)
        try:
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = parts
                return (int(year), int(month), int(day))
        except (ValueError, IndexError):
            pass
        return (0, 0, 0)

    def to_clipboard_text(self, transactions: List[BudgetTransaction]) -> str:
        """Generate text suitable for clipboard/paste.

        Args:
            transactions: List of BudgetTransaction objects.

        Returns:
            Tab-separated text for pasting into Google Sheets.
        """
        lines = []
        income = [tx for tx in transactions
                  if tx.transaction_type == TransactionType.INCOME]
        expenses = [tx for tx in transactions
                    if tx.transaction_type == TransactionType.EXPENSE]

        # Income section
        lines.append("Доход")
        lines.append("Чей\tДата\tСумма\tНазначение\tТег\tКомментарий")

        for tx in sorted(income, key=lambda x: self._parse_date_for_sort(x.date)):
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        lines.append("")
        lines.append("")

        # Expense section
        lines.append("Расход")
        lines.append("Чей\tДата\tСумма\tНазначение\tТег\tКомментарий")

        for tx in sorted(expenses, key=lambda x: self._parse_date_for_sort(x.date)):
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        return '\n'.join(lines)
