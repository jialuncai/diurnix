from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.executor import Executor
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec


def test_idempotency_key_rejects_different_arguments() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "echo",
            "Echo.",
            {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]},
            ("test.write",),
        ),
        lambda arguments: arguments["value"],
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    executor.execute(ToolCall("call_1", "echo", {"value": 1}), now, idempotency_key="same")
    with pytest.raises(ValidationError, match="different input"):
        executor.execute(ToolCall("call_2", "echo", {"value": 2}), now, idempotency_key="same")


def test_idempotency_argument_key_order_is_semantically_equal() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "echo",
            "Echo.",
            {"type": "object", "properties": {}, "additionalProperties": True},
            ("test.write",),
        ),
        lambda arguments: arguments,
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    first = executor.execute(
        ToolCall("call_1", "echo", {"a": 1, "b": 2}), now, idempotency_key="same"
    )
    second = executor.execute(
        ToolCall("call_2", "echo", {"b": 2, "a": 1}), now, idempotency_key="same"
    )
    assert second is first
