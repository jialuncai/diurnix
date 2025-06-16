from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect, PolicyEngine, PolicyRule
from diurnix.tools import SideEffect

ACTION = PolicyAction(
    "mail.send",
    ("mail.send",),
    SideEffect.EXTERNAL,
    {"to": "a@example.test"},
    datetime(2026, 10, 30, 8, tzinfo=UTC),
)


def test_policy_engine_uses_matching_rule_or_explicit_default() -> None:
    engine = PolicyEngine(
        (
            PolicyRule(
                "mail_approval", PolicyEffect.ASK, "mail needs approval", tools=("mail.send",)
            ),
        )
    )
    assert engine.decide(ACTION).effect is PolicyEffect.ASK
    other = PolicyAction("clock.now", ("clock.read",), SideEffect.NONE, {}, ACTION.occurred_at)
    assert engine.decide(other).effect is PolicyEffect.DENY
    assert engine.decide(other).rule_id == "default"


def test_policy_engine_rejects_duplicate_rule_identity() -> None:
    rule = PolicyRule("same", PolicyEffect.ALLOW, "same")
    with pytest.raises(ValidationError, match="unique"):
        PolicyEngine((rule, rule))
