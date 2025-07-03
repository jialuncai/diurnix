from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionStatus, Executor, RetryConfig
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def flaky_registry(failures: int, calls: list[int]) -> ToolRegistry:
    registry = ToolRegistry()

    def implementation(arguments: dict[str, object]) -> str:
        calls.append(len(calls) + 1)
        if len(calls) <= failures:
            raise RuntimeError("transient")
        return "ok"

    registry.register(
        ToolSpec("flaky", "Flaky.", {"type": "object", "properties": {}}, ("test.read",)),
        implementation,
    )
    return registry


def test_executor_retries_until_success_within_bound() -> None:
    calls: list[int] = []
    executor = Executor(
        flaky_registry(2, calls),
        PolicyEngine((), default_effect=PolicyEffect.ALLOW),
        RetryConfig(max_attempts=3),
    )
    receipt = executor.execute(ToolCall("call_1", "flaky", {}), NOW)
    assert receipt.status is ExecutionStatus.SUCCEEDED
    assert receipt.attempts == 3
    assert calls == [1, 2, 3]


def test_executor_stops_at_retry_bound() -> None:
    calls: list[int] = []
    executor = Executor(
        flaky_registry(5, calls),
        PolicyEngine((), default_effect=PolicyEffect.ALLOW),
        RetryConfig(max_attempts=2),
    )
    receipt = executor.execute(ToolCall("call_1", "flaky", {}), NOW)
    assert receipt.status is ExecutionStatus.FAILED
    assert receipt.attempts == 2
    assert calls == [1, 2]
