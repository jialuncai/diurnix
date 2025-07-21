from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import (
    Executor,
    executor_checkpoint,
    restore_executor_checkpoint,
    resume_batch,
)
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall
from diurnix.tools import ToolSpec

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
CALLS = tuple(ToolCall(f"call_{i}", "append", {"value": i}) for i in range(4))


def runtime(state: list[int]) -> Executor:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "append",
            "Append.",
            {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]},
            ("state.write",),
        ),
        lambda arguments: state.append(arguments["value"]) or list(state),
    )
    return Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))


def test_resume_batch_skips_previously_committed_side_effects() -> None:
    state: list[int] = []
    first = runtime(state)
    resume_batch(first, CALLS[:2], NOW)
    checkpoint = executor_checkpoint(first)
    recovered = runtime(state)
    restore_executor_checkpoint(recovered, checkpoint)
    receipts = resume_batch(recovered, CALLS, NOW)
    assert state == [0, 1, 2, 3]
    assert len(receipts) == 4
    assert receipts[:2] == tuple(first._idempotency[call.call_id] for call in CALLS[:2])
