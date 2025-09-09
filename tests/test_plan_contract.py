from __future__ import annotations

from diurnix.plan_validation import validate_plan
from diurnix.plans import Plan, PlanStep, ValueType


def test_complete_plan_validator_accepts_single_root() -> None:
    plan = Plan("plan", (PlanStep("now", "clock.now", {}, {}, {"time": ValueType.STRING}),))
    assert validate_plan(plan) is None
