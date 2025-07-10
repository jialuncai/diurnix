from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.approvals import ApprovalQueue, ApprovalStatus
from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_queue_records_approve_and_deny_outcomes() -> None:
    queue = ApprovalQueue()
    first = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    second = queue.submit(ToolCall("call_2", "mail.send", {}), NOW)
    approved = queue.decide(
        first.approval_id, True, NOW + timedelta(seconds=2), actor="user", reason="expected"
    )
    denied = queue.decide(
        second.approval_id, False, NOW + timedelta(seconds=3), actor="user", reason="unsafe"
    )
    assert approved.status is ApprovalStatus.APPROVED
    assert denied.status is ApprovalStatus.DENIED
    assert approved.decided_at == NOW + timedelta(seconds=2)
    assert queue.pending() == ()


def test_queue_rejects_unknown_resolved_and_blank_decisions() -> None:
    queue = ApprovalQueue()
    with pytest.raises(ValidationError, match="unknown"):
        queue.decide("missing", True, NOW, actor="user", reason="ok")
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    with pytest.raises(ValidationError, match="must not be blank"):
        queue.decide(record.approval_id, True, NOW, actor="", reason="ok")
    queue.decide(record.approval_id, True, NOW, actor="user", reason="ok")
    with pytest.raises(ValidationError, match="already resolved"):
        queue.decide(record.approval_id, False, NOW, actor="user", reason="changed")
