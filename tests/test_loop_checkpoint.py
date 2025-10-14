from __future__ import annotations

from diurnix.budgets import Budget, Usage
from diurnix.loop import LoopState
from diurnix.loop_runtime import BudgetedLoop, loop_checkpoint


def test_loop_checkpoint_captures_budget_and_usage() -> None:
    encoded = loop_checkpoint(
        BudgetedLoop(LoopState(step_count=2), Budget(5, 10, 3), Usage(2, 1, 1))
    )
    assert encoded["state"]["step_count"] == 2 and encoded["budget"]["max_steps"] == 5
    assert encoded["usage"] == {"steps": 2, "wall_seconds": 1, "money": 1}
