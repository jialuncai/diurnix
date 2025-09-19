from __future__ import annotations

from diurnix.plan_validation import topological_steps
from diurnix.planner import DeterministicPlanner
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def test_chained_planner_links_each_previous_result() -> None:
    r = ToolRegistry()
    for i in range(3):
        r.register(
            ToolSpec(f"tool_{i}", "Tool.", {"type": "object", "properties": {}}, (f"cap_{i}",)),
            lambda a: None,
        )
    plan = DeterministicPlanner(r).chained_plan(("cap_0", "cap_1", "cap_2"))
    assert topological_steps(plan) == ("step_0", "step_1", "step_2")
    assert plan.steps[2].inputs["previous"].step_id == "step_1"
