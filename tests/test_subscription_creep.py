from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.ledger_app import find_subscription_creep
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import plant_subscription_creep


def test_subscription_detector_recovers_each_planted_increase() -> None:
    transactions = plant_subscription_creep(
        create_persona(3), 3, datetime(2026, 1, 1, tzinfo=UTC), months=4
    )
    assert tuple(item.event_id for item in find_subscription_creep(transactions)) == (
        "txn_creep_3_1",
        "txn_creep_3_2",
        "txn_creep_3_3",
    )


def test_subscription_detector_validates_threshold() -> None:
    with pytest.raises(ValidationError, match="positive"):
        find_subscription_creep((), minimum_increase=0)


def test_stable_or_falling_subscription_is_not_creep() -> None:
    from dataclasses import replace

    planted = plant_subscription_creep(
        create_persona(3), 3, datetime(2026, 1, 1, tzinfo=UTC), months=3
    )
    stable = tuple(replace(item, amount=-18.0) for item in planted)
    assert find_subscription_creep(stable) == ()


def test_subscription_input_order_does_not_change_detection() -> None:
    transactions = plant_subscription_creep(
        create_persona(4), 4, datetime(2026, 1, 1, tzinfo=UTC), months=4
    )
    assert find_subscription_creep(transactions) == find_subscription_creep(
        tuple(reversed(transactions))
    )
