from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionStatus, Executor, RetryConfig, ToolTimeout
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec


def test_timeout_signal_produces_terminal_receipt_without_retry() -> None:
    attempts: list[int] = []
    registry = ToolRegistry()

    def timeout(arguments: dict[str, object]) -> None:
        attempts.append(1)
        raise ToolTimeout("deadline exceeded")

    registry.register(
        ToolSpec(
            "slow", "Synthetic timeout.", {"type": "object", "properties": {}}, ("test.read",)
        ),
        timeout,
    )
    executor = Executor(
        registry,
        PolicyEngine((), default_effect=PolicyEffect.ALLOW),
        RetryConfig(max_attempts=3),
    )
    receipt = executor.execute(
        ToolCall("call_1", "slow", {}), datetime(2026, 10, 30, 8, tzinfo=UTC)
    )
    assert receipt.status is ExecutionStatus.TIMED_OUT
    assert receipt.error == "deadline exceeded"
    assert receipt.attempts == 1
    assert attempts == [1]


def test_timeout_receipt_is_not_idempotency_cached() -> None:
    attempts: list[int] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec("slow", "Slow.", {"type": "object", "properties": {}}, ("test.read",)),
        lambda arguments: attempts.append(1) or (_ for _ in ()).throw(ToolTimeout()),
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    executor.execute(ToolCall("call_1", "slow", {}), now, idempotency_key="same")
    executor.execute(ToolCall("call_2", "slow", {}), now, idempotency_key="same")
    assert attempts == [1, 1]
