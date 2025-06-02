from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall, ToolResult, invoke_call
from diurnix.tools import ToolSpec


def test_typed_tool_call_correlates_result() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "math.double",
            "Double.",
            {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]},
            ("math.read",),
        ),
        lambda arguments: arguments["value"] * 2,
    )
    call = ToolCall("call_1", "math.double", {"value": 4})
    assert invoke_call(registry, call) == ToolResult("call_1", "math.double", 8)


def test_typed_call_validates_both_identifiers() -> None:
    import pytest

    with pytest.raises(ValueError, match="call_id"):
        ToolCall("Bad ID", "math.double", {})
    with pytest.raises(ValueError, match="tool"):
        ToolCall("call_1", "Bad Tool", {})
