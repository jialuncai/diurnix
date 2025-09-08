from __future__ import annotations

from diurnix.plan_validation import topological_steps
from diurnix.plans import InputRef, Plan, PlanStep, ValueType


def test_topological_order_is_dependency_then_lexical() -> None:
    a = PlanStep("a", "echo", {}, {}, {"out": ValueType.ANY})
    z = PlanStep("z", "echo", {}, {}, {"out": ValueType.ANY})
    end = PlanStep(
        "end",
        "echo",
        {},
        {"x": InputRef("a", "out"), "y": InputRef("z", "out")},
        {"out": ValueType.ANY},
    )
    assert topological_steps(Plan("plan", (end, z, a))) == ("a", "z", "end")
