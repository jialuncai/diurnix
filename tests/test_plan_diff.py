from __future__ import annotations

from diurnix.plans import Plan, PlanStep, ValueType, diff_plans


def step(name: str, tool: str = "a") -> PlanStep:
    return PlanStep(name, tool, {}, {}, {"out": ValueType.ANY})


def test_plan_diff_separates_added_removed_changed() -> None:
    before = Plan("before", (step("removed"), step("changed")))
    after = Plan("after", (step("added"), step("changed", "b")))
    assert diff_plans(before, after) == {
        "added": ("added",),
        "removed": ("removed",),
        "changed": ("changed",),
    }


def test_plan_diff_ignores_plan_identity_only() -> None:
    assert diff_plans(Plan("a", (step("same"),)), Plan("b", (step("same"),))) == {
        "added": (),
        "removed": (),
        "changed": (),
    }
