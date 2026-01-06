"""Data models for bank converter."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    """Type of transaction."""
    INCOME = "income"
    EXPENSE = "expense"
    SKIP = "skip"


@dataclass
class BankTransaction:
    """Raw transaction from bank export."""
    operation_date: str       # "Дата операции"
    payment_date: str         # "Дата платежа"
    card_number: str          # "Номер карты"
    status: str               # "Статус"
    amount: str               # "Сумма операции" (string with comma decimal)
    currency: str             # "Валюта операции"
    category: str             # "Категория"
    mcc: str                  # "MCC"
    description: str          # "Описание"


@dataclass
class BudgetTransaction:
    """Converted transaction for budget output."""
    owner: str                # "Чей"
    date: str                 # "Дата" (DD.MM.YYYY)
    amount: float             # "Сумма" (positive number)
    purpose: str              # "Назначение"
    tag: str                  # "Тег"
    comment: str              # "Комментарий"
    transaction_type: TransactionType


@dataclass
class UnknownMapping:
    """Represents an unknown category or vendor needing user input."""
    mapping_type: str         # "category" or "vendor"
    original_value: str       # The unknown category or vendor name
    suggested_tag: str        # Default suggestion
    suggested_purpose: str    # For vendors only

    def __hash__(self):
        return hash((self.mapping_type, self.original_value))

    def __eq__(self, other):
        if not isinstance(other, UnknownMapping):
            return False
        return (self.mapping_type == other.mapping_type and
                self.original_value == other.original_value)
