from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.approvals import ApprovalQueue, ApprovalStatus
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_approval_expires_at_inclusive_deadline() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW, ttl=timedelta(minutes=5))
    assert queue.expire(record.expires_at - timedelta(microseconds=1)) == ()
    expired = queue.expire(record.expires_at)
    assert len(expired) == 1
    assert expired[0].status is ApprovalStatus.EXPIRED
    assert expired[0].actor == "system"
    assert queue.pending() == ()


def test_expiry_is_idempotent() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    queue.expire(record.expires_at)
    assert queue.expire(record.expires_at + timedelta(days=1)) == ()
