from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def registry() -> ToolRegistry:
    result = ToolRegistry()
    for name, caps in (
        ("calendar.list", ("calendar.read",)),
        ("calendar.move", ("calendar.read", "calendar.write")),
        ("task.list", ("task.read",)),
    ):
        result.register(
            ToolSpec(name, f"Tool {name}.", {"type": "object", "properties": {}}, caps),
            lambda arguments: None,
        )
    return result


def test_capability_query_returns_lexically_ordered_matches() -> None:
    matches = registry().by_capability("calendar.read")
    assert [spec.name for spec in matches] == ["calendar.list", "calendar.move"]


def test_capability_query_supports_any_and_all_semantics() -> None:
    tools = registry()
    any_matches = tools.by_capability("calendar.write,task.read")
    assert [spec.name for spec in any_matches] == ["calendar.move", "task.list"]
    all_matches = tools.by_capability("calendar.read,calendar.write", require_all=True)
    assert [spec.name for spec in all_matches] == ["calendar.move"]


def test_capability_query_rejects_empty_request() -> None:
    with pytest.raises(ValidationError, match="must not be empty"):
        registry().by_capability(" , ")


def test_side_effect_query_is_explicit_and_empty_safe() -> None:
    from diurnix.tools import SideEffect, ToolSpec

    tools = registry()
    tools.register(
        ToolSpec(
            "mail.send",
            "Send mail.",
            {"type": "object", "properties": {}},
            ("mail.send",),
            SideEffect.EXTERNAL,
        ),
        lambda arguments: None,
    )
    assert [item.name for item in tools.by_side_effect(SideEffect.EXTERNAL)] == ["mail.send"]
    assert tools.by_side_effect() == ()
