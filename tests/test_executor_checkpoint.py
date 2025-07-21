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


def test_executor_checkpoint_restores_without_replaying_side_effect() -> None:
    from diurnix.executor import restore_executor_checkpoint

    original_calls: list[int] = []
    original = executor(original_calls)
    receipt = original.execute(ToolCall("call_1", "counter", {}), NOW, idempotency_key="key")
    recovered_calls: list[int] = []
    recovered = executor(recovered_calls)
    restore_executor_checkpoint(recovered, executor_checkpoint(original))
    replayed = recovered.execute(ToolCall("call_2", "counter", {}), NOW, idempotency_key="key")
    assert replayed == receipt
    assert recovered_calls == []


def test_executor_checkpoint_rejects_wrong_schema() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.executor import restore_executor_checkpoint

    with pytest.raises(ValidationError, match="match schema"):
        restore_executor_checkpoint(executor([]), {"schema_version": 2, "idempotency": []})
