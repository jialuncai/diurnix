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


def test_crash_resume_matches_uninterrupted_final_state() -> None:
    uninterrupted_state: list[int] = []
    uninterrupted = runtime(uninterrupted_state)
    uninterrupted_receipts = resume_batch(uninterrupted, CALLS, NOW)

    resumed_state: list[int] = []
    before_crash = runtime(resumed_state)
    resume_batch(before_crash, CALLS[:2], NOW)
    after_crash = runtime(resumed_state)
    restore_executor_checkpoint(after_crash, executor_checkpoint(before_crash))
    resumed_receipts = resume_batch(after_crash, CALLS, NOW)

    assert resumed_state == uninterrupted_state == [0, 1, 2, 3]
    assert [item.output for item in resumed_receipts] == [
        item.output for item in uninterrupted_receipts
    ]


def test_repeated_resume_is_idempotent() -> None:
    state: list[int] = []
    executor = runtime(state)
    first = resume_batch(executor, CALLS, NOW)
    second = resume_batch(executor, CALLS, NOW)
    assert second == first
    assert state == [0, 1, 2, 3]
