from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.approvals import ApproverMode, PendingApproval, ScriptedApprover
from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall

APPROVAL = PendingApproval(
    "approval_1",
    ToolCall("call_1", "mail.send", {}),
    datetime(2026, 10, 30, 8, tzinfo=UTC),
    datetime(2026, 10, 30, 9, tzinfo=UTC),
)


def test_scripted_approver_modes_are_explicit() -> None:
    assert ScriptedApprover("allow", ApproverMode.AUTO_ALLOW).response(APPROVAL) == (
        True,
        "scripted allow",
    )
    assert ScriptedApprover("deny", ApproverMode.AUTO_DENY).response(APPROVAL) == (
        False,
        "scripted deny",
    )
    assert ScriptedApprover("ask", ApproverMode.DEFER).response(APPROVAL) is None


def test_scripted_approver_validates_name_and_latency() -> None:
    with pytest.raises(ValidationError, match="invalid"):
        ScriptedApprover("", ApproverMode.DEFER)
    with pytest.raises(ValidationError, match="invalid"):
        ScriptedApprover("user", ApproverMode.DEFER, -1)


def test_scripted_approver_applies_simulated_latency() -> None:
    from diurnix.approvals import ApprovalQueue, ApprovalStatus, apply_scripted_approver

    queue = ApprovalQueue()
    record = queue.submit(APPROVAL.call, APPROVAL.created_at)
    changed = apply_scripted_approver(
        queue, record.approval_id, ScriptedApprover("persona", ApproverMode.AUTO_ALLOW, 2.5)
    )
    assert changed.status is ApprovalStatus.APPROVED
    assert changed.decided_at == record.created_at + timedelta(seconds=2.5)
    assert changed.actor == "persona"


def test_deferred_script_leaves_request_pending() -> None:
    from diurnix.approvals import ApprovalQueue, apply_scripted_approver

    queue = ApprovalQueue()
    record = queue.submit(APPROVAL.call, APPROVAL.created_at)
    assert (
        apply_scripted_approver(
            queue, record.approval_id, ScriptedApprover("persona", ApproverMode.DEFER)
        )
        is record
    )
