from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import AnomalyLabel
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_transaction

NOW = datetime(2026, 10, 1, 8, tzinfo=UTC)


def test_regular_transaction_is_seeded_and_unlabeled() -> None:
    persona = create_persona(3)
    first = generate_transaction(persona, 7, 0, NOW)
    assert first == generate_transaction(persona, 7, 0, NOW)
    assert first.planted_anomaly is AnomalyLabel.NONE
    assert first.amount < 0
    assert first.currency == "CNY"


def test_regular_transaction_stays_near_merchant_baseline() -> None:
    persona = create_persona(3)
    baselines = {merchant.name: merchant.typical_amount for merchant in persona.merchants}
    for index in range(50):
        transaction = generate_transaction(persona, 7, index, NOW)
        ratio = round(abs(transaction.amount) / baselines[transaction.merchant], 6)
        assert 0.8 <= ratio <= 1.2
