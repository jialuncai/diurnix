from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import AnomalyLabel
from diurnix.ledger_app import detect_ledger_anomalies
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month


def _findings():
    transactions = generate_planted_ledger_month(
        create_persona(5), 5, datetime(2026, 1, 1, tzinfo=UTC)
    )
    return detect_ledger_anomalies(transactions)


def test_unified_detector_recovers_each_anomaly_family() -> None:
    labels = {finding.label for finding in _findings()}
    assert labels == {
        AnomalyLabel.DUPLICATE,
        AnomalyLabel.OUTLIER,
        AnomalyLabel.SUBSCRIPTION_CREEP,
        AnomalyLabel.MISCATEGORIZED,
    }


def test_unified_findings_have_stable_identity_order() -> None:
    findings = _findings()
    assert tuple(item.transaction_id for item in findings) == tuple(
        sorted(item.transaction_id for item in findings)
    )
