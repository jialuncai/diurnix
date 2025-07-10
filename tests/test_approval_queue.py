from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.approvals import ApprovalQueue, ApprovalStatus
from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_approval_queue_submits_and_orders_pending_calls() -> None:
    queue = ApprovalQueue()
    later = queue.submit(ToolCall("call_2", "mail.send", {}), NOW + timedelta(seconds=1))
    earlier = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    assert queue.get(earlier.approval_id) is earlier
    assert queue.pending() == (earlier, later)
    assert all(item.status is ApprovalStatus.PENDING for item in queue.pending())


def test_approval_queue_rejects_duplicate_call_and_invalid_ttl() -> None:
    queue = ApprovalQueue()
    call = ToolCall("call_1", "mail.send", {})
    queue.submit(call, NOW)
    with pytest.raises(ValidationError, match="already exists"):
        queue.submit(call, NOW)
    with pytest.raises(ValidationError, match="TTL"):
        ApprovalQueue().submit(ToolCall("call_2", "mail.send", {}), NOW, ttl=timedelta(0))
