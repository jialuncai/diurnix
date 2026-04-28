from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import Transaction
from diurnix.ledger_app import categorize_transaction


def _transaction(merchant: str, category: str = "wrong"):
    return Transaction("txn", datetime(2026, 1, 1, tzinfo=UTC), -10, "CNY", merchant, category)


def test_category_result_ignores_stored_category_field() -> None:
    result = categorize_transaction(_transaction("合成市场", "transport"))
    assert result.category == "groceries"
    assert result.confidence == 0.99 and result.tells == ("市场",)


def test_uncued_category_result_has_low_confidence() -> None:
    result = categorize_transaction(_transaction("Unknown"))
    assert result.category == "other" and result.confidence == 0.25
