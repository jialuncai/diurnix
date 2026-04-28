from __future__ import annotations

from datetime import UTC, datetime

from diurnix.ledger_app import category_metrics
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_ledger_month


def test_category_metrics_use_executed_synthetic_transactions() -> None:
    persona = create_persona(8)
    transactions = generate_ledger_month(persona, 8, datetime(2026, 1, 1, tzinfo=UTC), days=5)
    metrics = category_metrics(transactions)
    assert metrics == {"sample_count": 10, "accuracy": 1.0, "uncertain_count": 0, "synthetic": True}


def test_empty_category_metrics_are_explicit() -> None:
    assert category_metrics(()) == {
        "sample_count": 0,
        "accuracy": 0.0,
        "uncertain_count": 0,
        "synthetic": True,
    }
