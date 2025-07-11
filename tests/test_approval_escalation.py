from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.approvals import ApprovalQueue, ApprovalStatus, escalate
from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_escalation_records_actor_time_and_level() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    escalated = escalate(queue, record.approval_id, NOW, actor="supervisor")
    assert escalated.status is ApprovalStatus.ESCALATED
    assert escalated.escalation_level == 1
    assert escalated.actor == "supervisor"
    assert queue.pending() == ()


def test_only_pending_approval_can_escalate() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    queue.decide(record.approval_id, False, NOW, actor="user", reason="no")
    with pytest.raises(ValidationError, match="only pending"):
        escalate(queue, record.approval_id, NOW, actor="supervisor")
