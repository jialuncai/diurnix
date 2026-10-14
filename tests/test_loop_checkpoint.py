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


def test_loop_checkpoint_roundtrips_runtime_values() -> None:
    from diurnix.loop_runtime import loop_from_checkpoint

    loop = BudgetedLoop(
        LoopState(step_count=2, observations=("x",), receipts=("r",)),
        Budget(5, 10, 3),
        Usage(2, 1, 1),
    )
    assert loop_from_checkpoint(loop_checkpoint(loop)) == loop


def test_loop_checkpoint_rejects_non_mapping_sections() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.loop_runtime import loop_from_checkpoint

    with pytest.raises(ValidationError, match="invalid loop checkpoint"):
        loop_from_checkpoint({"schema_version": 1, "state": [], "budget": {}, "usage": {}})
