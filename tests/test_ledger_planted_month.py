from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import AnomalyLabel
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month

START = datetime(2026, 10, 1, 8, tzinfo=UTC)


def test_planted_ledger_contains_every_anomaly_family() -> None:
    transactions = generate_planted_ledger_month(create_persona(3), 7, START)
    labels = {item.planted_anomaly for item in transactions}
    assert labels == set(AnomalyLabel)
    assert len({item.event_id for item in transactions}) == len(transactions)


def test_planted_ledger_is_seed_reproducible_and_ordered() -> None:
    first = generate_planted_ledger_month(create_persona(3), 7, START)
    second = generate_planted_ledger_month(create_persona(3), 7, START)
    assert first == second
    assert list(first) == sorted(first, key=lambda item: (item.occurred_at, item.event_id))
