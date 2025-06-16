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


def test_higher_priority_rule_wins_regardless_of_effect() -> None:
    engine = PolicyEngine(
        (
            PolicyRule("low_deny", PolicyEffect.DENY, "low", priority=1),
            PolicyRule("high_allow", PolicyEffect.ALLOW, "high", priority=2),
        )
    )
    assert engine.decide(ACTION).rule_id == "high_allow"


def test_equal_priority_prefers_deny_then_ask_then_allow() -> None:
    rules = (
        PolicyRule("allow", PolicyEffect.ALLOW, "allow", priority=5),
        PolicyRule("ask", PolicyEffect.ASK, "ask", priority=5),
        PolicyRule("deny", PolicyEffect.DENY, "deny", priority=5),
    )
    assert PolicyEngine(rules).decide(ACTION).rule_id == "deny"
    assert PolicyEngine(rules[:2]).decide(ACTION).rule_id == "ask"


def test_policy_decision_copies_action_arguments() -> None:
    decision = PolicyEngine((), default_effect=PolicyEffect.ALLOW).decide(ACTION)
    decision.redacted_arguments["to"] = "changed"
    assert ACTION.arguments == {"to": "a@example.test"}
