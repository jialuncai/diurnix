from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.planner import DeterministicPlanner
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def registry() -> ToolRegistry:
    r = ToolRegistry()
    r.register(
        ToolSpec("clock.now", "Now.", {"type": "object", "properties": {}}, ("clock.read",)),
        lambda a: None,
    )
    return r


def test_planner_resolves_unique_capability() -> None:
    assert DeterministicPlanner(registry()).resolve("clock.read").name == "clock.now"


def test_planner_reports_missing_capability() -> None:
    with pytest.raises(ValidationError, match="no tool"):
        DeterministicPlanner(registry()).resolve("mail.send")


def test_planner_rejects_ambiguous_capability() -> None:
    tools = registry()
    tools.register(
        ToolSpec("clock.other", "Other.", {"type": "object", "properties": {}}, ("clock.read",)),
        lambda a: None,
    )
    with pytest.raises(ValidationError, match="ambiguous"):
        DeterministicPlanner(tools).resolve("clock.read")
