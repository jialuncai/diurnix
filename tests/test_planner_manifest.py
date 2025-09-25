from __future__ import annotations

from diurnix.planner import DeterministicPlanner, planner_manifest
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def test_planner_manifest_is_reproducible() -> None:
    r = ToolRegistry()
    r.register(
        ToolSpec("clock.now", "Now.", {"type": "object", "properties": {}}, ("clock.read",)),
        lambda a: None,
    )
    p = DeterministicPlanner(r)
    assert planner_manifest(p, ("clock.read",)) == planner_manifest(p, ("clock.read",))
    assert planner_manifest(p, ("clock.read",))["output"]["step_count"] == 1
