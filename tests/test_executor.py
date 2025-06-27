from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionStatus, Executor
from diurnix.policy import PolicyEffect, PolicyEngine, PolicyRule
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def registry(calls: list[dict[str, object]]) -> ToolRegistry:
    result = ToolRegistry()
    result.register(
        ToolSpec(
            "math.double",
            "Double.",
            {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]},
            ("math.read",),
        ),
        lambda arguments: calls.append(arguments) or arguments["value"] * 2,
    )
    return result


def test_executor_invokes_allowed_tool_once() -> None:
    calls: list[dict[str, object]] = []
    policy = PolicyEngine((PolicyRule("allow", PolicyEffect.ALLOW, "allowed"),))
    receipt = Executor(registry(calls), policy).execute(
        ToolCall("call_1", "math.double", {"value": 4}), NOW
    )
    assert receipt.status is ExecutionStatus.SUCCEEDED
    assert receipt.output == 8
    assert receipt.attempts == 1
    assert calls == [{"value": 4}]
    assert receipt.receipt_id.startswith("receipt_")
