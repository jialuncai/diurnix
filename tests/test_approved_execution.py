from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.approvals import ApprovalQueue
from diurnix.errors import ValidationError
from diurnix.executor import ExecutionStatus, Executor, execute_approved
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_approved_call_executes_once_and_restores_policy() -> None:
    calls: list[int] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec("sample", "Sample.", {"type": "object", "properties": {}}, ("test.write",)),
        lambda arguments: calls.append(1) or "ok",
    )
    deny = PolicyEngine((), default_effect=PolicyEffect.DENY)
    executor = Executor(registry, deny)
    queue = ApprovalQueue()
    pending = queue.submit(ToolCall("call_1", "sample", {}), NOW)
    approved = queue.decide(pending.approval_id, True, NOW, actor="user", reason="ok")
    receipt = execute_approved(executor, approved, NOW)
    assert receipt.status is ExecutionStatus.SUCCEEDED
    assert calls == [1]
    assert executor.policy is deny


def test_nonapproved_record_cannot_resume_execution() -> None:
    queue = ApprovalQueue()
    pending = queue.submit(ToolCall("call_1", "sample", {}), NOW)
    with pytest.raises(ValidationError, match="not approved"):
        execute_approved(Executor(ToolRegistry(), PolicyEngine(())), pending, NOW)
