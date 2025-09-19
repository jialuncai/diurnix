from __future__ import annotations

from diurnix.planner import DeterministicPlanner
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def test_planner_keeps_goal_order_and_stable_identity() -> None:
    r = ToolRegistry()
    for name, cap in (("clock.now", "clock.read"), ("task.list", "task.read")):
        r.register(
            ToolSpec(name, name + ".", {"type": "object", "properties": {}}, (cap,)), lambda a: None
        )
    first = DeterministicPlanner(r).plan(("task.read", "clock.read"))
    second = DeterministicPlanner(r).plan(("task.read", "clock.read"))
    assert [s.tool for s in first.steps] == ["task.list", "clock.now"]
    assert first == second and first.plan_id.startswith("plan_")
