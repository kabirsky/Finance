"""
Data models for bank converter.

=== LEARNING: Python Module Docstrings ===
This triple-quoted string at the top is a "docstring" - documentation that becomes
part of the module. You can access it with: import models; print(models.__doc__)

[JS] Like JSDoc comments, but built into the language
[C++] Like Doxygen comments, but actually useful at runtime
"""

# =============================================================================
# IMPORTS
# =============================================================================
# [JS] Similar to: import { dataclass } from 'dataclasses';
# [C++] Similar to: #include <dataclass>
#
# Python's import system:
#   from X import Y    - import specific item Y from module X
#   import X           - import entire module, access as X.something

from dataclasses import dataclass  # Decorator for auto-generating class boilerplate
from enum import Enum              # Base class for enumerations
from typing import Optional        # Type hint: "can be this type OR None"


# =============================================================================
# ENUM EXAMPLE
# =============================================================================
class TransactionType(Enum):
    """
    Type of transaction.

    === LEARNING: Python Enums ===
    [JS] Similar to: const TransactionType = { INCOME: 'income', ... }
         But safer - you can't accidentally use a wrong string.

    [C++] Similar to: enum class TransactionType { INCOME, EXPENSE, SKIP };
          But each value can have associated data (here, strings).

    Usage:
        tx_type = TransactionType.INCOME
        tx_type.value  # Returns "income"
        tx_type.name   # Returns "INCOME"

    Comparison:
        tx_type == TransactionType.INCOME  # True
        tx_type == "income"                # False! Compare with enum, not string
    """
    INCOME = "income"
    EXPENSE = "expense"
    SKIP = "skip"


# =============================================================================
# DATACLASS EXAMPLES
# =============================================================================
@dataclass
class BankTransaction:
    """
    Raw transaction from bank export.

    === LEARNING: @dataclass Decorator ===
    The @dataclass decorator automatically generates:
    - __init__() constructor
    - __repr__() for printing (like toString())
    - __eq__() for comparison

    [JS/TS] This is like a TypeScript interface + class combined:
        interface BankTransaction {
            operation_date: string;
            payment_date: string;
            // ...
        }

    [C++] Like a struct with auto-generated constructors:
        struct BankTransaction {
            std::string operation_date;
            std::string payment_date;
            // ...
        };

    Without @dataclass, you'd write:
        class BankTransaction:
            def __init__(self, operation_date, payment_date, ...):
                self.operation_date = operation_date
                self.payment_date = payment_date
                # ... tedious!

    === LEARNING: Type Hints ===
    The `: str` after each field is a TYPE HINT.
    - NOT enforced at runtime (Python is dynamically typed)
    - Helps IDEs with autocomplete
    - Can be checked with tools like mypy
    - Like TypeScript annotations, but optional

    [JS] Similar to TypeScript: operation_date: string
    [C++] Similar to: std::string operation_date (but not enforced!)
    """
    # Each line defines a field with its type
    # Format: field_name: type
    operation_date: str       # "Дата операции"
    payment_date: str         # "Дата платежа"
    card_number: str          # "Номер карты"
    status: str               # "Статус"
    amount: str               # "Сумма операции" (string with comma decimal)
    currency: str             # "Валюта операции"
    category: str             # "Категория"
    mcc: str                  # "MCC"
    description: str          # "Описание"

    # Usage example (not actual code, just for learning):
    # tx = BankTransaction(
    #     operation_date="27.12.2025",
    #     payment_date="27.12.2025",
    #     card_number="*1234",
    #     status="OK",
    #     amount="-1000,00",
    #     currency="RUB",
    #     category="Супермаркеты",
    #     mcc="5411",
    #     description="Пятёрочка"
    # )


@dataclass
class BudgetTransaction:
    """
    Converted transaction for budget output.

    This is what we transform BankTransaction into - the format
    suitable for Google Sheets.
    """
    owner: str                # "Чей" - whose transaction
    date: str                 # "Дата" (DD.MM.YYYY)
    amount: float             # "Сумма" (positive number)
    purpose: str              # "Назначение" - what was it for
    tag: str                  # "Тег" - category tag
    comment: str              # "Комментарий"
    transaction_type: TransactionType  # Using our enum type!

    # Note: This field uses another class as its type (TransactionType)
    # [JS] Like: transactionType: TransactionType
    # [C++] Like: TransactionType transaction_type;


@dataclass
class UnknownMapping:
    """
    Represents an unknown category or vendor needing user input.

    When we encounter a bank category or vendor we don't know how to map,
    we create one of these to ask the user.

    === LEARNING: Custom Methods in Dataclass ===
    Even with @dataclass, you can add custom methods!
    """
    mapping_type: str         # "category" or "vendor"
    original_value: str       # The unknown category or vendor name
    suggested_tag: str        # Default suggestion
    suggested_purpose: str    # For vendors only

    def __hash__(self):
        """
        === LEARNING: __hash__ (Dunder Methods) ===
        Methods with double underscores are "dunder" (double-under) methods.
        They're Python's way of implementing operator overloading and protocols.

        __hash__ makes this object usable in sets and as dict keys.
        It must return an integer.

        [JS] Similar to implementing a custom valueOf() for use in Set
        [C++] Similar to overloading std::hash<T>

        The hash() function creates a hash from any hashable value.
        Tuples are hashable, so we create a tuple of our key fields.
        """
        return hash((self.mapping_type, self.original_value))

    def __eq__(self, other):
        """
        === LEARNING: __eq__ (Equality Comparison) ===
        Defines behavior for == operator.

        [JS] Similar to implementing custom equals() method
        [C++] Similar to overloading operator==

        isinstance(obj, Class) checks if obj is an instance of Class.
        [JS] Like: obj instanceof Class
        [C++] Like: dynamic_cast<Class*>(obj) != nullptr
        """
        # First check if 'other' is even the right type
        if not isinstance(other, UnknownMapping):
            return False
        # Then compare the relevant fields
        # Note: 'and' instead of '&&'
        return (self.mapping_type == other.mapping_type and
                self.original_value == other.original_value)

    # Note: When you define __hash__ and __eq__, objects can be used in sets:
    # unknown_set = {UnknownMapping(...), UnknownMapping(...)}
    # Duplicates (same mapping_type and original_value) are automatically removed!
