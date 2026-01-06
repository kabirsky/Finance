"""
Output writer for budget data.

=== LEARNING: This module demonstrates ===
- Lambda functions (anonymous functions)
- sorted() with custom key functions
- The csv module for writing
- List comprehensions with conditions
- String joining and formatting
- Tuple unpacking
"""

# =============================================================================
# IMPORTS
# =============================================================================
import csv
from typing import List

from .models import BudgetTransaction, TransactionType


class BudgetWriter:
    """
    Writes converted data to CSV for Google Sheets.

    === LEARNING: Class with only methods, no state ===
    This class has no __init__ and no instance variables.
    It's essentially a namespace for related functions.

    [C++] Like a class with only static methods, or a namespace:
          namespace BudgetWriter {
              void write(const std::vector<BudgetTransaction>& txs, const std::string& path);
          }

    In Python, you COULD make these standalone functions, but grouping
    them in a class provides organization and discoverability.
    """

    def write(self, transactions: List[BudgetTransaction], output_path: str):
        """
        Write transactions to CSV file.

        Args:
            transactions: List of BudgetTransaction objects.
            output_path: Path to output CSV file.
        """
        # === LEARNING: List comprehension with condition ===
        # [expression for item in list if condition]
        # This is like filter + map combined!
        #
        # [C++] Like:
        #       std::vector<BudgetTransaction> income;
        #       std::copy_if(txs.begin(), txs.end(), std::back_inserter(income),
        #                    [](const auto& tx) { return tx.type == INCOME; });
        income = [tx for tx in transactions
                  if tx.transaction_type == TransactionType.INCOME]
        expenses = [tx for tx in transactions
                    if tx.transaction_type == TransactionType.EXPENSE]

        # === LEARNING: Context manager for file writing ===
        # newline='' is important for csv module on Windows
        # (prevents extra blank lines between rows)
        # [C++] Similar to std::ofstream with RAII
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            # === LEARNING: csv.writer ===
            # Creates a writer that handles CSV escaping, quoting, etc.
            # [C++] No standard equivalent - you'd use a library or write manually
            writer = csv.writer(f)

            # Write income section
            self._write_section(writer, "Доход", income)

            # Empty rows between sections
            # writerow([]) writes an empty line
            writer.writerow([])
            writer.writerow([])

            # Write expense section
            self._write_section(writer, "Расход", expenses)

    def _write_section(
        self, writer: csv.writer, title: str, transactions: List[BudgetTransaction]
    ):
        """
        Write a section (income or expense).

        === LEARNING: Type hints for library objects ===
        csv.writer is the type of the writer object.
        Python's type system accepts class names as types.

        Args:
            writer: CSV writer object.
            title: Section title ("Доход" or "Расход").
            transactions: List of transactions for this section.
        """
        # writerow() takes a list/iterable and writes as CSV row
        writer.writerow([title])
        writer.writerow(["Чей", "Дата", "Сумма", "Назначение", "Тег", "Комментарий"])

        # === LEARNING: sorted() with key function ===
        # sorted() returns a NEW sorted list (original unchanged)
        # key= specifies a function that extracts comparison key
        #
        # [C++] Like:
        #       auto sorted_txs = transactions;
        #       std::sort(sorted_txs.begin(), sorted_txs.end(),
        #                 [this](const auto& a, const auto& b) {
        #                     return parse_date(a.date) < parse_date(b.date);
        #                 });
        #
        # === LEARNING: Lambda functions ===
        # lambda x: expression
        # Creates an anonymous function that takes x and returns expression
        #
        # [C++] Like: [](const auto& x) { return expression; }
        # [JS] Like: (x) => expression
        #
        # Lambdas in Python are limited to SINGLE expressions.
        # For complex logic, use a regular function.
        sorted_transactions = sorted(
            transactions,
            key=lambda x: self._parse_date_for_sort(x.date)
        )

        for tx in sorted_transactions:
            # === LEARNING: Building a list for writerow ===
            # writerow expects an iterable of values
            writer.writerow([
                tx.owner,
                tx.date,
                self._format_amount(tx.amount),
                tx.purpose,
                tx.tag,
                tx.comment
            ])

    def _format_amount(self, amount: float) -> str:
        """
        Format amount for output.

        Uses integer format for whole numbers, otherwise 2 decimal places.

        === LEARNING: Number formatting ===
        Python has powerful string formatting:
        - f"{value:.2f}" = 2 decimal places
        - f"{value:,}" = thousands separator
        - f"{value:>10}" = right-align in 10 chars

        [C++] Like std::setprecision and std::fixed with streams,
              or std::format in C++20

        Args:
            amount: Amount to format.

        Returns:
            Formatted amount string.
        """
        # === LEARNING: Float to int comparison ===
        # amount == int(amount) checks if amount is a whole number
        # [C++] Like: amount == static_cast<int>(amount)
        #       or: std::floor(amount) == amount
        if amount == int(amount):
            return str(int(amount))

        # === LEARNING: f-string formatting ===
        # {value:.2f} formats as float with 2 decimal places
        # Then replace '.' with ',' for Russian locale
        # [C++] Like: std::format("{:.2f}", amount) then replace
        return f"{amount:.2f}".replace('.', ',')

    def _parse_date_for_sort(self, date_str: str) -> tuple:
        """
        Parse date string for sorting.

        === LEARNING: Returning tuples for comparison ===
        Tuples compare element-by-element (lexicographically).
        (2025, 12, 27) > (2025, 12, 26) because of the last element.
        (2025, 12, 27) < (2026, 1, 1) because 2025 < 2026.

        [C++] Like std::tuple with operator< - compares lexicographically

        Args:
            date_str: Date in DD.MM.YYYY format.

        Returns:
            Tuple (year, month, day) for sorting.
        """
        if not date_str:
            return (0, 0, 0)  # Empty dates sort first

        # === LEARNING: Exception handling for parsing ===
        # [C++] Like try/catch with specific exception types
        try:
            # .split('.') returns ["27", "12", "2025"]
            parts = date_str.split('.')
            if len(parts) == 3:
                # === LEARNING: Tuple unpacking ===
                # Assign multiple values at once from a list/tuple
                # [C++] Like std::tie(day, month, year) = parts; (but cleaner!)
                day, month, year = parts
                # Return tuple with year first for chronological sorting
                return (int(year), int(month), int(day))
        except (ValueError, IndexError):
            # === LEARNING: Catching multiple exception types ===
            # Use tuple of exception types in except clause
            # [C++] Like: catch (const std::invalid_argument&) { }
            #             catch (const std::out_of_range&) { }
            # Python allows combining: except (Type1, Type2)
            pass

        # Default for unparseable dates
        return (0, 0, 0)

    def to_clipboard_text(self, transactions: List[BudgetTransaction]) -> str:
        """
        Generate text suitable for clipboard/paste.

        === LEARNING: String building patterns ===
        Building a large string from parts:
        1. Append to list, then join (EFFICIENT - used here)
        2. Concatenate with += (SLOW for many strings)

        [C++] Like using std::ostringstream or collecting in vector<string>
              then joining, rather than repeated string concatenation

        Args:
            transactions: List of BudgetTransaction objects.

        Returns:
            Tab-separated text for pasting into Google Sheets.
        """
        # === LEARNING: List for string building ===
        # Appending to list is O(1), joining at end is efficient
        # [C++] Like: std::vector<std::string> lines; then join with "\n"
        lines = []

        # Separate income and expenses
        income = [tx for tx in transactions
                  if tx.transaction_type == TransactionType.INCOME]
        expenses = [tx for tx in transactions
                    if tx.transaction_type == TransactionType.EXPENSE]

        # Income section header
        lines.append("Доход")
        # \t = tab character for spreadsheet column separation
        lines.append("Чей\tДата\tСумма\tНазначение\tТег\tКомментарий")

        # === LEARNING: sorted() inline ===
        # Can call sorted() directly in the for loop
        # [C++] Would need to sort first or use ranges::views
        for tx in sorted(income, key=lambda x: self._parse_date_for_sort(x.date)):
            # === LEARNING: f-string with \t (tabs) ===
            # Building tab-separated row
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        # Empty lines between sections
        lines.append("")
        lines.append("")

        # Expense section
        lines.append("Расход")
        lines.append("Чей\tДата\tСумма\tНазначение\tТег\tКомментарий")

        for tx in sorted(expenses, key=lambda x: self._parse_date_for_sort(x.date)):
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        # === LEARNING: str.join() ===
        # '\n'.join(list) concatenates list elements with '\n' between them
        # [C++] No direct equivalent. You'd loop or use boost::algorithm::join
        # [JS] Like: lines.join('\n')
        #
        # Note: The separator goes BETWEEN elements, not at the end
        return '\n'.join(lines)

    def to_clipboard_text_income(self, transactions: List[BudgetTransaction]) -> str:
        """
        Generate clipboard text for INCOME transactions only.

        === LEARNING: Focused method for specific use case ===
        This method generates ONLY the data rows (no headers) for income,
        ready to paste directly into the income section of Google Sheets.

        Args:
            transactions: List of BudgetTransaction objects.

        Returns:
            Tab-separated text with income data rows only.
        """
        # Filter income transactions only
        income = [tx for tx in transactions
                  if tx.transaction_type == TransactionType.INCOME]

        # Build lines - DATA ONLY, no section header or column headers
        lines = []
        for tx in sorted(income, key=lambda x: self._parse_date_for_sort(x.date)):
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        return '\n'.join(lines)

    def to_clipboard_text_expenses(self, transactions: List[BudgetTransaction]) -> str:
        """
        Generate clipboard text for EXPENSE transactions only.

        === LEARNING: Parallel method for expenses ===
        Same logic as to_clipboard_text_income but for expenses.
        Having separate methods is cleaner than adding a parameter.

        Args:
            transactions: List of BudgetTransaction objects.

        Returns:
            Tab-separated text with expense data rows only.
        """
        # Filter expense transactions only
        expenses = [tx for tx in transactions
                    if tx.transaction_type == TransactionType.EXPENSE]

        # Build lines - DATA ONLY, no section header or column headers
        lines = []
        for tx in sorted(expenses, key=lambda x: self._parse_date_for_sort(x.date)):
            lines.append(f"{tx.owner}\t{tx.date}\t{self._format_amount(tx.amount)}\t"
                        f"{tx.purpose}\t{tx.tag}\t{tx.comment}")

        return '\n'.join(lines)
