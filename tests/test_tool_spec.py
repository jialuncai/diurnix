from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tools import SideEffect, ToolSpec


def spec(**changes: object) -> ToolSpec:
    values: dict[str, object] = {
        "name": "calendar.create",
        "description": "Create a synthetic calendar entry.",
        "arguments": {"type": "object", "properties": {}},
        "capabilities": ("calendar.write",),
    }
    values.update(changes)
    return ToolSpec(**values)  # type: ignore[arg-type]


def test_tool_spec_preserves_policy_metadata() -> None:
    tool = spec(side_effect=SideEffect.EXTERNAL, version=2)
    assert tool.name == "calendar.create"
    assert tool.side_effect is SideEffect.EXTERNAL
    assert tool.version == 2


def test_tool_spec_validates_name_description_and_version() -> None:
    with pytest.raises(ValueError, match="tool name"):
        spec(name="Bad Tool")
    with pytest.raises(ValidationError, match="description"):
        spec(description=" ")
    with pytest.raises(ValidationError, match="version"):
        spec(version=0)


def test_tool_spec_requires_unique_portable_capabilities() -> None:
    with pytest.raises(ValidationError, match="nonempty and unique"):
        spec(capabilities=())
    with pytest.raises(ValidationError, match="nonempty and unique"):
        spec(capabilities=("calendar.read", "calendar.read"))
    with pytest.raises(ValueError, match="capability"):
        spec(capabilities=("Calendar Read",))


def test_tool_spec_requires_object_argument_root() -> None:
    for schema in ({}, {"type": "array"}, {"type": "string"}):
        with pytest.raises(ValidationError, match="object type"):
            spec(arguments=schema)


def test_side_effect_wire_values_are_exhaustive() -> None:
    assert [item.value for item in SideEffect] == ["none", "local", "external", "money"]
