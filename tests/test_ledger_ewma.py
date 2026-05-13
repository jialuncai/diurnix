from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import Transaction
from diurnix.ledger_app import ewma_deviations

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _transaction(event_id: str, day: int, amount: float):
    return Transaction(
        event_id, NOW + timedelta(days=day), amount, "CNY", "合成视频", "subscriptions"
    )


def test_ewma_deviation_compares_to_prior_baseline() -> None:
    scores = ewma_deviations((_transaction("a", 0, -20), _transaction("b", 1, -30)))
    assert scores["a"] == 0.0 and scores["b"] == 0.5


def test_ewma_validates_alpha() -> None:
    with pytest.raises(ValidationError, match="between"):
        ewma_deviations((), alpha=0)
