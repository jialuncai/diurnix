from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import Transaction
from diurnix.ledger_app import monthly_ledger_summary


def test_monthly_summary_aggregates_executed_categories() -> None:
    transactions = (
        Transaction("a", datetime(2026, 1, 1, tzinfo=UTC), -20, "CNY", "合成市场", "x"),
        Transaction("b", datetime(2026, 1, 2, tzinfo=UTC), -5, "CNY", "合成地铁", "x"),
    )
    summary = monthly_ledger_summary(transactions, ())
    assert summary["total_spending"] == 25
    assert summary["category_spending"] == {"groceries": 20.0, "transport": 5.0}
    assert summary["synthetic"] is True


def test_empty_monthly_summary_has_zero_totals() -> None:
    assert monthly_ledger_summary((), ()) == {
        "transaction_count": 0,
        "total_spending": 0,
        "category_spending": {},
        "anomaly_count": 0,
        "synthetic": True,
    }
