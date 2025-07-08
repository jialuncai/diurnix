from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionStatus, Executor, execute_batch
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec


def test_batch_stops_at_first_failure_with_prior_state_intact() -> None:
    state: list[str] = []
    registry = ToolRegistry()

    def run(arguments: dict[str, object]) -> None:
        value = str(arguments["value"])
        if value == "fail":
            raise RuntimeError("synthetic")
        state.append(value)

    registry.register(
        ToolSpec(
            "append",
            "Append.",
            {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
            ("state.write",),
        ),
        run,
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    calls = tuple(
        ToolCall(f"call_{i}", "append", {"value": value})
        for i, value in enumerate(("one", "fail", "three"))
    )
    receipts = execute_batch(executor, calls, datetime(2026, 10, 30, 8, tzinfo=UTC))
    assert [item.status for item in receipts] == [ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED]
    assert state == ["one"]


def test_batch_can_collect_independent_failures_when_configured() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("fail", "Fail.", {"type": "object", "properties": {}}, ("test.read",)),
        lambda arguments: (_ for _ in ()).throw(RuntimeError("x")),
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    calls = (ToolCall("call_1", "fail", {}), ToolCall("call_2", "fail", {}))
    assert (
        len(
            execute_batch(
                executor, calls, datetime(2026, 10, 30, 8, tzinfo=UTC), stop_on_failure=False
            )
        )
        == 2
    )
