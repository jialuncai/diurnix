from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plans import Plan, PlanStep, ValueType


def item(identity: str = "one", budget: float = 0) -> PlanStep:
    return PlanStep(identity, "clock.now", {}, {}, {"value": ValueType.STRING}, money_budget=budget)


def test_plan_sums_quantized_budget() -> None:
    assert Plan("plan_1", (item("a", 0.1), item("b", 0.2))).total_money_budget == 0.3


def test_plan_requires_steps_unique_ids_and_current_version() -> None:
    with pytest.raises(ValidationError, match="at least one"):
        Plan("plan_1", ())
    with pytest.raises(ValidationError, match="unique"):
        Plan("plan_1", (item(), item()))
    with pytest.raises(ValidationError, match="unsupported"):
        Plan("plan_1", (item(),), 2)
