from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import AnomalyLabel, EventKind, Transaction

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def transaction(**changes: object) -> Transaction:
    values: dict[str, object] = {
        "event_id": "txn_1",
        "occurred_at": NOW,
        "amount": -23.5,
        "currency": "CNY",
        "merchant": "Synthetic Market",
        "category": "groceries",
    }
    values.update(changes)
    return Transaction(**values)  # type: ignore[arg-type]


def test_transaction_supports_expense_and_refund_signs() -> None:
    expense = transaction(amount=-10.0)
    refund = transaction(amount=10.0, planted_anomaly=AnomalyLabel.DUPLICATE)
    assert expense.kind is EventKind.TRANSACTION
    assert expense.amount == -10.0
    assert refund.amount == 10.0
    assert refund.planted_anomaly is AnomalyLabel.DUPLICATE


def test_transaction_rejects_zero_and_nonfinite_amounts() -> None:
    for amount in (0.0, float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValidationError, match="finite and nonzero"):
            transaction(amount=amount)


def test_transaction_requires_portable_currency_code() -> None:
    for currency in ("cny", "CN", "CNY1", "¥¥¥"):
        with pytest.raises(ValidationError, match="currency"):
            transaction(currency=currency)


def test_transaction_anomaly_labels_cover_factory_cases() -> None:
    assert [label.value for label in AnomalyLabel] == [
        "none",
        "duplicate",
        "outlier",
        "subscription_creep",
        "miscategorized",
    ]


def test_transaction_rejects_blank_merchant_or_category() -> None:
    with pytest.raises(ValidationError, match="merchant and category"):
        transaction(merchant="  ")
    with pytest.raises(ValidationError, match="merchant and category"):
        transaction(category="")


def test_transaction_keeps_decimal_input_precision_supplied_by_factory() -> None:
    assert transaction(amount=-12.345678).amount == -12.345678
