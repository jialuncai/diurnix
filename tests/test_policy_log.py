from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.policy import PolicyDecision, PolicyEffect
from diurnix.policy_log import DecisionLog

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
DECISION = PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {})


def test_decision_log_append_returns_new_contiguous_history() -> None:
    empty = DecisionLog()
    first = empty.append(NOW, "mail.send", DECISION)
    second = first.append(NOW, "ledger.pay", DECISION)
    assert empty.records == ()
    assert [record.sequence for record in second.records] == [0, 1]
    assert [record.action_tool for record in second.records] == ["mail.send", "ledger.pay"]


def test_decision_log_rejects_naive_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        DecisionLog().append(datetime(2026, 10, 30, 8), "mail.send", DECISION)
