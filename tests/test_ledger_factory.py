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


def test_ledger_month_has_two_ordered_unique_expenses_per_day() -> None:
    from diurnix.synthetic_ledger import generate_ledger_month

    transactions = generate_ledger_month(create_persona(3), 7, NOW)
    assert len(transactions) == 60
    assert len({transaction.event_id for transaction in transactions}) == 60
    assert list(transactions) == sorted(transactions, key=lambda item: item.occurred_at)


def test_ledger_month_validates_day_count() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.synthetic_ledger import generate_ledger_month

    for days in (0, 32):
        with pytest.raises(ValidationError, match="one to 31"):
            generate_ledger_month(create_persona(3), 7, NOW, days=days)
