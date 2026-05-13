from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.ledger_app import find_zscore_outliers
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month


def test_zscore_detector_finds_planted_outlier() -> None:
    transactions = generate_planted_ledger_month(
        create_persona(3), 3, datetime(2026, 1, 1, tzinfo=UTC)
    )
    detected = {item.event_id for item in find_zscore_outliers(transactions, threshold=2.5)}
    assert "txn_outlier_3" in detected


def test_zscore_detector_validates_threshold() -> None:
    with pytest.raises(ValidationError, match="positive"):
        find_zscore_outliers((), threshold=0)
