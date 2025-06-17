from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect, PolicyEngine
from diurnix.policy_rules import money_approval
from diurnix.tools import SideEffect


def action(amount: object) -> PolicyAction:
    return PolicyAction(
        "ledger.pay",
        ("money.write",),
        SideEffect.MONEY,
        {"amount": amount},
        datetime(2026, 10, 30, 8, tzinfo=UTC),
    )


def test_money_threshold_matches_absolute_inclusive_boundary() -> None:
    engine = PolicyEngine((money_approval(100),), default_effect=PolicyEffect.ALLOW)
    assert engine.decide(action(99.99)).effect is PolicyEffect.ALLOW
    assert engine.decide(action(100)).effect is PolicyEffect.ASK
    assert engine.decide(action(-100)).effect is PolicyEffect.ASK


def test_money_threshold_ignores_bool_and_missing_amount() -> None:
    rule = money_approval(1)
    assert not rule.matches(action(True))
    assert not rule.matches(action("100"))


def test_money_threshold_rejects_negative_configuration() -> None:
    with pytest.raises(ValidationError, match="cannot be negative"):
        money_approval(-1)
