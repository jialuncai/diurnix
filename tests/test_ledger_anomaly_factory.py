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


def test_outlier_anomaly_scales_expense_magnitude() -> None:
    from diurnix.synthetic_ledger import plant_outlier

    source = generate_transaction(create_persona(3), 7, 0, NOW)
    outlier = plant_outlier(source, 7, multiplier=10)
    assert outlier.amount == round(source.amount * 10, 2)
    assert outlier.planted_anomaly is AnomalyLabel.OUTLIER


def test_outlier_multiplier_must_exceed_one() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.synthetic_ledger import plant_outlier

    source = generate_transaction(create_persona(3), 7, 0, NOW)
    with pytest.raises(ValidationError, match="exceed one"):
        plant_outlier(source, 7, multiplier=1)


def test_subscription_creep_has_monotonic_magnitude_and_labels() -> None:
    from diurnix.synthetic_ledger import plant_subscription_creep

    transactions = plant_subscription_creep(create_persona(3), 7, NOW)
    magnitudes = [abs(item.amount) for item in transactions]
    assert magnitudes == sorted(magnitudes)
    assert transactions[0].planted_anomaly is AnomalyLabel.NONE
    assert all(item.planted_anomaly is AnomalyLabel.SUBSCRIPTION_CREEP for item in transactions[1:])


def test_miscategorization_changes_only_identity_category_and_truth() -> None:
    from diurnix.synthetic_ledger import plant_miscategorization

    source = generate_transaction(create_persona(3), 7, 0, NOW)
    anomaly = plant_miscategorization(source, 7)
    assert anomaly.event_id != source.event_id
    assert anomaly.category != source.category
    assert anomaly.amount == source.amount
    assert anomaly.merchant == source.merchant
    assert anomaly.planted_anomaly is AnomalyLabel.MISCATEGORIZED
