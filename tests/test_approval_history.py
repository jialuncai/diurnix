from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.approvals import ApprovalQueue, ApprovalStatus
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_history_retains_resolved_and_pending_records() -> None:
    queue = ApprovalQueue()
    approved = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    pending = queue.submit(ToolCall("call_2", "mail.send", {}), NOW + timedelta(seconds=1))
    queue.decide(approved.approval_id, True, NOW, actor="user", reason="ok")
    history = queue.history()
    assert [item.status for item in history] == [ApprovalStatus.APPROVED, ApprovalStatus.PENDING]
    assert history[1] is pending
