from __future__ import annotations

from datetime import UTC, datetime

from diurnix.ledger_app import anomaly_metrics, detect_ledger_anomalies
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month


def test_anomaly_metrics_are_derived_from_planted_truth() -> None:
    transactions = generate_planted_ledger_month(
        create_persona(7), 7, datetime(2026, 1, 1, tzinfo=UTC)
    )
    metrics = anomaly_metrics(transactions, detect_ledger_anomalies(transactions))
    assert metrics["synthetic"] is True and metrics["truth_count"] == 6
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0


def test_empty_anomaly_truth_has_defined_metrics() -> None:
    metrics = anomaly_metrics((), ())
    assert metrics["precision"] == 0.0 and metrics["recall"] == 1.0
