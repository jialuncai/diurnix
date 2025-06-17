from __future__ import annotations

from datetime import UTC, datetime, time

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect
from diurnix.policy_rules import OutsideTimeWindowRule
from diurnix.tools import SideEffect


def rule() -> OutsideTimeWindowRule:
    return OutsideTimeWindowRule(
        "quiet_hours",
        PolicyEffect.ASK,
        "outside work hours",
        starts_at=time(9),
        ends_at=time(18),
        timezone="Asia/Shanghai",
    )


def action(hour: int) -> PolicyAction:
    return PolicyAction(
        "mail.send", (), SideEffect.EXTERNAL, {}, datetime(2026, 10, 30, hour, tzinfo=UTC)
    )


def test_time_window_uses_local_half_open_bounds() -> None:
    policy = rule()
    assert policy.matches(action(0))
    assert not policy.matches(action(1))
    assert not policy.matches(action(9))
    assert policy.matches(action(10))


def test_time_window_validates_range_and_timezone() -> None:
    with pytest.raises(ValidationError, match="positive"):
        OutsideTimeWindowRule("bad", PolicyEffect.DENY, "bad", starts_at=time(9), ends_at=time(9))
    with pytest.raises(ValidationError, match="timezone"):
        OutsideTimeWindowRule("bad", PolicyEffect.DENY, "bad", timezone="Mars/Base")
