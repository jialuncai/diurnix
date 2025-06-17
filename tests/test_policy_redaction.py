from __future__ import annotations

from datetime import UTC, datetime

from diurnix.policy import PolicyAction, PolicyEffect, PolicyEngine
from diurnix.redaction import contains_pii
from diurnix.tools import SideEffect


def test_policy_decision_always_carries_redacted_arguments() -> None:
    action = PolicyAction(
        "mail.send",
        ("mail.send",),
        SideEffect.EXTERNAL,
        {"to": "person@example.test", "body": "call +86 138 0013 8000"},
        datetime(2026, 10, 30, 8, tzinfo=UTC),
    )
    decision = PolicyEngine((), default_effect=PolicyEffect.ALLOW).decide(action)
    assert decision.redacted_arguments == {"to": "[EMAIL]", "body": "call [PHONE]"}
    assert not contains_pii(decision.redacted_arguments)
    assert contains_pii(action.arguments)
