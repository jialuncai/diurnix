from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import AnomalyLabel
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month, ledger_ground_truth

START = datetime(2026, 10, 1, 8, tzinfo=UTC)


def test_ledger_truth_excludes_ordinary_transactions() -> None:
    transactions = generate_planted_ledger_month(create_persona(3), 7, START)
    truth = ledger_ground_truth(transactions)
    assert truth["transaction_count"] == len(transactions)
    expected = {
        item.event_id: item.planted_anomaly.value
        for item in transactions
        if item.planted_anomaly is not AnomalyLabel.NONE
    }
    assert truth["anomaly_ids"] == expected
    assert truth["anomaly_count"] == len(expected)
