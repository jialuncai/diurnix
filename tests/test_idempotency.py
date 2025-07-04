from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import Executor
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import SideEffect, ToolSpec


def test_idempotency_key_reuses_success_receipt_and_side_effect() -> None:
    calls: list[int] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "counter.add",
            "Add.",
            {"type": "object", "properties": {}},
            ("counter.write",),
            SideEffect.LOCAL,
        ),
        lambda arguments: calls.append(1) or len(calls),
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    first = executor.execute(ToolCall("call_1", "counter.add", {}), now, idempotency_key="key-1")
    second = executor.execute(ToolCall("call_2", "counter.add", {}), now, idempotency_key="key-1")
    assert second is first
    assert calls == [1]
    assert first.idempotency_key == "key-1"


def test_different_idempotency_keys_execute_independently() -> None:
    calls: list[int] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec("counter", "Count.", {"type": "object", "properties": {}}, ("counter.write",)),
        lambda arguments: calls.append(1),
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    for index in range(2):
        executor.execute(
            ToolCall(f"call_{index}", "counter", {}), now, idempotency_key=f"key-{index}"
        )
    assert calls == [1, 1]
