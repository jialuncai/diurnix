from __future__ import annotations

import random

from diurnix.budgets import Budget, Usage
from diurnix.loop import LoopState
from diurnix.loop_runtime import BudgetedLoop, consume


def test_seeded_usage_sequences_never_exceed_budget() -> None:
    source = random.Random(20261030)
    budget = Budget(20, 50, 30)
    loop = BudgetedLoop(LoopState(), budget)
    for _ in range(500):
        loop = consume(loop, Usage(source.randrange(3), source.random() * 3, source.random() * 2))
        assert budget.allows(loop.usage)


def test_stopped_loop_usage_remains_at_last_valid_value() -> None:
    loop = BudgetedLoop(LoopState(), Budget(0, 0, 0))
    changed = consume(loop, Usage(1, 1, 1))
    assert changed.usage == Usage()
