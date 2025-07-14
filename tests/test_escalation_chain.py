from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.approvals import (
    ApprovalQueue,
    ApprovalStatus,
    ApproverMode,
    ScriptedApprover,
    run_escalation_chain,
)
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_escalation_chain_stops_at_first_deciding_approver() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    result = run_escalation_chain(
        queue,
        record.approval_id,
        (
            ScriptedApprover("first", ApproverMode.DEFER, 1),
            ScriptedApprover("second", ApproverMode.AUTO_ALLOW, 2),
            ScriptedApprover("third", ApproverMode.AUTO_DENY, 10),
        ),
    )
    assert result.status is ApprovalStatus.APPROVED
    assert result.actor == "second"
    assert result.decided_at == NOW + timedelta(seconds=3)


def test_all_deferred_chain_escalates() -> None:
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    result = run_escalation_chain(
        queue, record.approval_id, (ScriptedApprover("ask", ApproverMode.DEFER, 4),)
    )
    assert result.status is ApprovalStatus.ESCALATED
    assert result.decided_at == NOW + timedelta(seconds=4)
