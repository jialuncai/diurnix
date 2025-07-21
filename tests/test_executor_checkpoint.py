from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import Executor, executor_checkpoint
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def executor(calls: list[int]) -> Executor:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("counter", "Count.", {"type": "object", "properties": {}}, ("state.write",)),
        lambda arguments: calls.append(1) or len(calls),
    )
    return Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))


def test_executor_checkpoint_contains_only_successful_keys() -> None:
    calls: list[int] = []
    runtime = executor(calls)
    runtime.execute(ToolCall("call_1", "counter", {}), NOW, idempotency_key="b")
    runtime.execute(ToolCall("call_2", "counter", {}), NOW, idempotency_key="a")
    checkpoint = executor_checkpoint(runtime)
    assert [item["key"] for item in checkpoint["idempotency"]] == ["a", "b"]
    assert all(item["receipt"]["status"] == "succeeded" for item in checkpoint["idempotency"])
