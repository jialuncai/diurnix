from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plan_validation import validate_conditions
from diurnix.plans import Plan, PlanStep, ValueType


def test_conditions_accumulate_in_topological_order() -> None:
    first = PlanStep("first", "a", {}, {}, {"x": ValueType.ANY}, effects=("loaded",))
    second = PlanStep("second", "b", {}, {}, {"y": ValueType.ANY}, preconditions=("loaded",))
    assert validate_conditions(Plan("plan", (first, second))) is None


def test_conditions_accept_initial_facts_and_reject_missing() -> None:
    step = PlanStep("step", "a", {}, {}, {"x": ValueType.ANY}, preconditions=("approved",))
    assert validate_conditions(Plan("plan", (step,)), ("approved",)) is None
    with pytest.raises(ValidationError, match="unsatisfied"):
        validate_conditions(Plan("plan", (step,)))
