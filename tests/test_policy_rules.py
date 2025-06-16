from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect, PolicyRule
from diurnix.tools import SideEffect

ACTION = PolicyAction(
    "mail.send",
    ("mail.send", "pii.write"),
    SideEffect.EXTERNAL,
    {},
    datetime(2026, 10, 30, 8, tzinfo=UTC),
)


def test_policy_rule_matches_each_nonempty_selector() -> None:
    assert PolicyRule("all", PolicyEffect.ALLOW, "default").matches(ACTION)
    assert PolicyRule("tool", PolicyEffect.ALLOW, "tool", tools=("mail.send",)).matches(ACTION)
    assert PolicyRule("cap", PolicyEffect.ALLOW, "cap", capabilities=("pii.write",)).matches(ACTION)
    both = PolicyRule(
        "both", PolicyEffect.ALLOW, "both", tools=("mail.send",), capabilities=("pii.write",)
    )
    assert both.matches(ACTION)
    assert not PolicyRule("miss", PolicyEffect.ALLOW, "miss", tools=("task.list",)).matches(ACTION)


def test_policy_rule_validates_identity_and_reason() -> None:
    with pytest.raises(ValueError, match="rule_id"):
        PolicyRule("Bad Rule", PolicyEffect.DENY, "bad")
    with pytest.raises(ValidationError, match="reason"):
        PolicyRule("rule", PolicyEffect.DENY, " ")
