from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.approvals import ApprovalStatus, PendingApproval
from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
CALL = ToolCall("call_1", "mail.send", {"text": "hello"})


def test_pending_approval_preserves_call_and_expiry() -> None:
    approval = PendingApproval("approval_1", CALL, NOW, NOW + timedelta(minutes=5))
    assert approval.status is ApprovalStatus.PENDING
    assert approval.call is CALL
    assert approval.decided_at is None
    assert [item.value for item in ApprovalStatus] == [
        "pending",
        "approved",
        "denied",
        "expired",
        "escalated",
    ]


def test_pending_approval_validates_expiry_and_level() -> None:
    with pytest.raises(ValidationError, match="follow creation"):
        PendingApproval("approval_1", CALL, NOW, NOW)
    with pytest.raises(ValidationError, match="cannot be negative"):
        PendingApproval("approval_1", CALL, NOW, NOW + timedelta(1), escalation_level=-1)
