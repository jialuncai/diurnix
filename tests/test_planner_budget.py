from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.planner import allocate_money_budget
from diurnix.plans import Plan, PlanStep, ValueType


def test_budget_allocator_preserves_quantized_total() -> None:
    plan = Plan(
        "plan", tuple(PlanStep(f"s{i}", "tool", {}, {}, {"x": ValueType.ANY}) for i in range(3))
    )
    changed = allocate_money_budget(plan, 1.0)
    assert [s.money_budget for s in changed.steps] == [0.333333, 0.333333, 0.333334]
    assert changed.total_money_budget == 1.0


def test_budget_allocator_rejects_negative() -> None:
    plan = Plan("plan", (PlanStep("s", "tool", {}, {}, {"x": ValueType.ANY}),))
    with pytest.raises(ValidationError, match="negative"):
        allocate_money_budget(plan, -1)
