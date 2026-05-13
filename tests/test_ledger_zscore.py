from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import Transaction
from diurnix.ledger_app import category_zscores


def _transaction(event_id: str, amount: float):
    return Transaction(
        event_id, datetime(2026, 1, 1, tzinfo=UTC), amount, "CNY", "合成市场", "groceries"
    )


def test_category_zscores_center_equal_values_at_zero() -> None:
    scores = category_zscores((_transaction("a", -10), _transaction("b", -10)))
    assert scores == {"a": 0.0, "b": 0.0}


def test_category_zscores_make_large_expense_positive() -> None:
    items = (
        *(_transaction(f"n-{index}", -10) for index in range(5)),
        _transaction("large", -100),
    )
    scores = category_zscores(items)
    assert scores["large"] > 2
    assert all(scores[f"n-{index}"] < 0 for index in range(5))
