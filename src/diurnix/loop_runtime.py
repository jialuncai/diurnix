"""Budgeted loop runtime helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from diurnix.budgets import Budget, Usage, reserve
from diurnix.loop import LoopState, stop_loop


@dataclass(frozen=True, slots=True)
class BudgetedLoop:
    state: LoopState
    budget: Budget
    usage: Usage = field(default_factory=Usage)


def consume(loop: BudgetedLoop, requested: Usage) -> BudgetedLoop:
    try:
        updated = reserve(loop.budget, loop.usage, requested)
    except Exception:
        return BudgetedLoop(
            stop_loop(loop.state, "resource budget exhausted"), loop.budget, loop.usage
        )
    return BudgetedLoop(loop.state, loop.budget, updated)


def run_cycle(
    state: LoopState, event: object, plan: object, receipt: object, observation: object
) -> LoopState:
    from diurnix.loop import attach_plan, observe, perceive, record_action
    from diurnix.plans import Plan

    if not isinstance(plan, Plan):
        from diurnix.errors import ValidationError

        raise ValidationError("loop cycle requires a plan")
    return observe(record_action(attach_plan(perceive(state, event), plan), receipt), observation)


def apply_receipt_stop(state: LoopState, status: str) -> LoopState:
    terminal = {
        "denied": "policy denied",
        "pending": "approval pending",
        "cancelled": "cancelled",
        "timed_out": "timed out",
        "failed": "tool failed",
    }
    return stop_loop(state, terminal[status]) if status in terminal else state


def loop_checkpoint(loop: BudgetedLoop) -> dict[str, object]:
    return {
        "schema_version": 1,
        "state": {
            "phase": loop.state.phase.value,
            "step_count": loop.state.step_count,
            "observations": list(loop.state.observations),
            "stop_reason": loop.state.stop_reason,
            "receipts": list(loop.state.receipts),
        },
        "budget": {
            "max_steps": loop.budget.max_steps,
            "max_wall_seconds": loop.budget.max_wall_seconds,
            "max_money": loop.budget.max_money,
        },
        "usage": {
            "steps": loop.usage.steps,
            "wall_seconds": loop.usage.wall_seconds,
            "money": loop.usage.money,
        },
    }


def loop_from_checkpoint(value: dict[str, object]) -> BudgetedLoop:
    from diurnix.errors import ValidationError
    from diurnix.loop import LoopPhase

    if (
        set(value) != {"schema_version", "state", "budget", "usage"}
        or value.get("schema_version") != 1
    ):
        raise ValidationError("loop checkpoint does not match schema")
    try:
        s = value["state"]
        b = value["budget"]
        u = value["usage"]
        if not isinstance(s, dict) or not isinstance(b, dict) or not isinstance(u, dict):
            raise TypeError("checkpoint sections must be mappings")
        state = LoopState(
            LoopPhase(s["phase"]),
            s["step_count"],
            tuple(s["observations"]),
            s["stop_reason"],
            None,
            tuple(s["receipts"]),
        )
        return BudgetedLoop(
            state,
            Budget(b["max_steps"], b["max_wall_seconds"], b["max_money"]),
            Usage(u["steps"], u["wall_seconds"], u["money"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid loop checkpoint payload") from error
