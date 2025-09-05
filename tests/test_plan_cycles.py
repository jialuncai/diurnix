from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plan_validation import validate_acyclic
from diurnix.plans import InputRef, Plan, PlanStep, ValueType


def node(name: str, dep: str) -> PlanStep:
    return PlanStep(name, "echo", {}, {"x": InputRef(dep, "out")}, {"out": ValueType.ANY})


def test_cycle_validator_rejects_two_node_cycle() -> None:
    with pytest.raises(ValidationError, match="cycle"):
        validate_acyclic(Plan("plan", (node("a", "b"), node("b", "a"))))


def test_cycle_validator_accepts_dependency_chain() -> None:
    root = PlanStep("root", "echo", {}, {}, {"out": ValueType.ANY})
    assert validate_acyclic(Plan("plan", (root, node("b", "root"), node("c", "b")))) is None
