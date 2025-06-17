from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect
from diurnix.policy_rules import RecipientAllowlistRule
from diurnix.tools import SideEffect

RULE = RecipientAllowlistRule(
    "recipient_deny",
    PolicyEffect.DENY,
    "recipient not allowed",
    allowed=("friend@example.test",),
    capabilities=("mail.send",),
)


def action(recipients: object) -> PolicyAction:
    return PolicyAction(
        "mail.send",
        ("mail.send",),
        SideEffect.EXTERNAL,
        {"recipients": recipients},
        datetime(2026, 10, 30, 8, tzinfo=UTC),
    )


def test_recipient_rule_accepts_case_insensitive_allowlist() -> None:
    assert not RULE.matches(action(["FRIEND@example.test"]))
    assert RULE.matches(action(["friend@example.test", "other@example.test"]))
    assert not RULE.matches(action("friend@example.test"))


def test_recipient_rule_conservatively_matches_invalid_shape() -> None:
    assert RULE.matches(action({"email": "friend@example.test"}))
    with pytest.raises(ValidationError, match="must not be empty"):
        RecipientAllowlistRule("empty", PolicyEffect.DENY, "empty")
