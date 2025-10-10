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
