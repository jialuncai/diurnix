from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionStatus, Executor
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_executor_converts_tool_exception_to_failure_receipt() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("broken", "Break.", {"type": "object", "properties": {}}, ("test.read",)),
        lambda arguments: (_ for _ in ()).throw(RuntimeError("synthetic failure")),
    )
    receipt = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW)).execute(
        ToolCall("call_1", "broken", {}), NOW
    )
    assert receipt.status is ExecutionStatus.FAILED
    assert receipt.error == "RuntimeError: synthetic failure"
    assert receipt.output is None
    assert receipt.attempts == 1
