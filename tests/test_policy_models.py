from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyDecision, PolicyEffect
from diurnix.tools import SideEffect


def test_policy_models_preserve_effect_context() -> None:
    action = PolicyAction(
        "mail.send",
        ("mail.send",),
        SideEffect.EXTERNAL,
        {"to": "a@example.test"},
        datetime(2026, 10, 30, 8, tzinfo=UTC),
    )
    decision = PolicyDecision(
        PolicyEffect.ASK, "external_mail", "approval required", action.arguments
    )
    assert action.side_effect is SideEffect.EXTERNAL
    assert decision.effect is PolicyEffect.ASK
    assert [item.value for item in PolicyEffect] == ["allow", "ask", "deny"]


def test_policy_action_requires_aware_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        PolicyAction("mail.send", (), SideEffect.NONE, {}, datetime(2026, 10, 30))
