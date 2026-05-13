from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import Transaction
from diurnix.ledger_app import find_duplicate_transactions

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _transaction(event_id: str, minute: int, merchant: str = "Market"):
    return Transaction(event_id, NOW + timedelta(minutes=minute), -42, "CNY", merchant, "groceries")


def test_duplicate_detector_accepts_near_merchant_name() -> None:
    first, second = _transaction("a", 0), _transaction("b", 3, "Markets")
    assert find_duplicate_transactions((second, first)) == ((first, second),)


def test_duplicate_detector_rejects_distant_time() -> None:
    assert find_duplicate_transactions((_transaction("a", 0), _transaction("b", 20))) == ()


def test_duplicate_detector_validates_thresholds() -> None:
    with pytest.raises(ValidationError, match="negative"):
        find_duplicate_transactions((), minutes=-1)
