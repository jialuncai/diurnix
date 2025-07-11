from __future__ import annotations

from datetime import UTC, datetime

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
