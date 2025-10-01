from __future__ import annotations

from diurnix.budgets import Budget, Usage
from diurnix.loop import LoopPhase, LoopState
from diurnix.loop_runtime import BudgetedLoop, consume


def test_loop_usage_consumes_all_dimensions() -> None:
    loop = BudgetedLoop(LoopState(), Budget(3, 10, 5))
    changed = consume(loop, Usage(1, 2, 3))
    assert changed.usage == Usage(1, 2, 3) and changed.state.phase is LoopPhase.PERCEIVE


def test_loop_usage_stops_without_overcharging() -> None:
    loop = BudgetedLoop(LoopState(), Budget(1, 1, 1), Usage(1, 0, 0))
    changed = consume(loop, Usage(1, 0, 0))
    assert changed.state.phase is LoopPhase.STOPPED and changed.usage == loop.usage
