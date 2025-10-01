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
