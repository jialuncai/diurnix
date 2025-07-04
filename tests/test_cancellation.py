from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import CancellationToken, ExecutionStatus, Executor
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec


def test_cancelled_token_prevents_tool_invocation() -> None:
    calls: list[int] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec("sample", "Sample.", {"type": "object", "properties": {}}, ("test.write",)),
        lambda arguments: calls.append(1),
    )
    token = CancellationToken()
    token.cancel("user stopped")
    receipt = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW)).execute(
        ToolCall("call_1", "sample", {}), datetime(2026, 10, 30, 8, tzinfo=UTC), cancellation=token
    )
    assert receipt.status is ExecutionStatus.CANCELLED
    assert receipt.error == "user stopped"
    assert receipt.attempts == 0
    assert calls == []


def test_live_token_does_not_change_execution() -> None:
    token = CancellationToken()
    assert token.cancelled is False
    token.cancel()
    assert token.cancelled is True and token.reason == "cancelled"
