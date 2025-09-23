from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.planner import replace_step_tool
from diurnix.plans import Plan, PlanStep, ValueType


def test_replanning_replaces_only_requested_tool() -> None:
    plan = Plan(
        "plan",
        (
            PlanStep("a", "old", {}, {}, {"x": ValueType.ANY}),
            PlanStep("b", "same", {}, {}, {"x": ValueType.ANY}),
        ),
    )
    changed = replace_step_tool(plan, "a", "new")
    assert [s.tool for s in changed.steps] == ["new", "same"] and plan.steps[0].tool == "old"


def test_replanning_rejects_unknown_step() -> None:
    plan = Plan("plan", (PlanStep("a", "old", {}, {}, {"x": ValueType.ANY}),))
    with pytest.raises(ValidationError, match="unknown"):
        replace_step_tool(plan, "missing", "new")


def test_observation_violation_preserves_declared_order() -> None:
    from diurnix.planner import violated_preconditions

    step = PlanStep(
        "a", "tool", {}, {}, {"x": ValueType.ANY}, preconditions=("online", "approved", "fresh")
    )
    assert violated_preconditions(step, ("approved",)) == ("online", "fresh")
    assert violated_preconditions(step, ("online", "approved", "fresh")) == ()
