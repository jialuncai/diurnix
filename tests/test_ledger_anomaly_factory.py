from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import AnomalyLabel
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_transaction, plant_duplicate

NOW = datetime(2026, 10, 1, 8, tzinfo=UTC)


def test_duplicate_anomaly_matches_source_and_has_new_identity() -> None:
    source = generate_transaction(create_persona(3), 7, 0, NOW)
    duplicate = plant_duplicate(source, 7)
    assert duplicate.event_id != source.event_id
    assert duplicate.amount == source.amount
    assert duplicate.merchant == source.merchant
    assert duplicate.planted_anomaly is AnomalyLabel.DUPLICATE
    assert (duplicate.occurred_at - source.occurred_at).total_seconds() == 180
