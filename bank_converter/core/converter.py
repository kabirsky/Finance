"""Main conversion logic for bank data."""

from typing import List, Tuple, Set

from .models import BankTransaction, BudgetTransaction, TransactionType, UnknownMapping
from .reader import parse_amount, parse_date
from ..config.manager import ConfigManager


class BankConverter:
    """Converts bank transactions to budget format."""

    def __init__(self, config: ConfigManager):
        """Initialize converter with config.

        Args:
            config: ConfigManager instance with mappings.
        """
        self.config = config
        self.unknown_mappings: List[UnknownMapping] = []
        self._seen_unknowns: Set[Tuple[str, str]] = set()

    def convert(
        self, transactions: List[BankTransaction]
    ) -> Tuple[List[BudgetTransaction], List[UnknownMapping]]:
        """Convert bank transactions to budget format.

        Args:
            transactions: List of BankTransaction objects.

        Returns:
            Tuple of (converted transactions, unknown mappings needing user input).
        """
        self.unknown_mappings = []
        self._seen_unknowns = set()
        result = []

        for tx in transactions:
            budget_tx = self._convert_single(tx)
            if budget_tx:
                result.append(budget_tx)

        return result, self.unknown_mappings

    def _convert_single(self, tx: BankTransaction) -> BudgetTransaction | None:
        """Convert a single bank transaction.

        Args:
            tx: BankTransaction to convert.

        Returns:
            BudgetTransaction or None if should be skipped.
        """
        # Skip failed transactions
        if tx.status != "OK":
            return None

        # Skip internal transfers
        if tx.description in self.config.skip_descriptions:
            return None

        # Parse amount
        amount = parse_amount(tx.amount)

        # Skip zero amounts
        if amount == 0:
            return None

        # Determine transaction type
        tx_type = self._determine_type(amount, tx.category)

        if tx_type == TransactionType.SKIP:
            return None

        # Get tag and purpose
        tag, purpose = self._get_mapping(tx.category, tx.description)

        # Create budget transaction
        return BudgetTransaction(
            owner=self.config.owner,
            date=parse_date(tx.operation_date),
            amount=abs(amount),
            purpose=purpose,
            tag=tag,
            comment="",
            transaction_type=tx_type
        )

    def _determine_type(self, amount: float, category: str) -> TransactionType:
        """Determine if transaction is income, expense, or should be skipped.

        Args:
            amount: Transaction amount (positive or negative).
            category: Bank category.

        Returns:
            TransactionType enum value.
        """
        # Income categories are always income regardless of sign
        if category in self.config.income_categories:
            return TransactionType.INCOME

        if amount > 0:
            return TransactionType.INCOME
        elif amount < 0:
            return TransactionType.EXPENSE

        return TransactionType.SKIP

    def _get_mapping(self, category: str, description: str) -> Tuple[str, str]:
        """Get tag and purpose for a transaction.

        Args:
            category: Bank category.
            description: Transaction description (vendor name).

        Returns:
            Tuple of (tag, purpose/name).
        """
        # First check vendor overrides (higher priority)
        if description in self.config.vendor_overrides:
            override = self.config.vendor_overrides[description]
            return override["tag"], override.get("назначение", description)

        # Then check category mappings
        if category in self.config.category_mappings:
            tag = self.config.category_mappings[category]
            return tag, description

        # Unknown - add to list for user resolution
        self._add_unknown(category, description)
        return "Неизвестно", description

    def _add_unknown(self, category: str, description: str):
        """Track unknown mappings for user resolution.

        Args:
            category: Unknown bank category.
            description: Vendor/person description.
        """
        # Track if we've already added this
        key = ("category", category)
        if category and category not in self.config.category_mappings:
            if key not in self._seen_unknowns:
                self._seen_unknowns.add(key)
                unknown = UnknownMapping(
                    mapping_type="category",
                    original_value=category,
                    suggested_tag="Неизвестно",
                    suggested_purpose=""
                )
                self.unknown_mappings.append(unknown)

        # For "Переводы" category, also track vendor for potential override
        # This helps identify recurring transfers to specific people
        if category == "Переводы":
            key = ("vendor", description)
            if description and description not in self.config.vendor_overrides:
                if key not in self._seen_unknowns:
                    self._seen_unknowns.add(key)
                    unknown = UnknownMapping(
                        mapping_type="vendor",
                        original_value=description,
                        suggested_tag="Неизвестно",
                        suggested_purpose=description
                    )
                    self.unknown_mappings.append(unknown)
