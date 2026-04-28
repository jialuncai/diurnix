from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import Transaction
from diurnix.ledger_app import BudgetEnvelope, apply_expense


def _transaction(merchant: str, amount: float = -42):
    return Transaction("txn", datetime(2026, 1, 1, tzinfo=UTC), amount, "CNY", merchant, "stored")


def test_expense_updates_matching_envelope_immutably() -> None:
    original = BudgetEnvelope("groceries", 100)
    updated = apply_expense(original, _transaction("合成市场"))
    assert updated.spent == 42 and updated.available == 58
    assert original.spent == 0


def test_expense_rejects_category_mismatch_and_income() -> None:
    with pytest.raises(ValidationError, match="belong"):
        apply_expense(BudgetEnvelope("transport", 100), _transaction("合成市场"))
    with pytest.raises(ValidationError, match="negative"):
        apply_expense(BudgetEnvelope("groceries", 100), _transaction("合成市场", 42))
