from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec

SPEC = ToolSpec(
    "task.list", "List local tasks.", {"type": "object", "properties": {}}, ("task.read",)
)


def test_registry_registers_and_requires_spec() -> None:
    registry = ToolRegistry()
    registry.register(SPEC, lambda arguments: [])
    assert registry.get("task.list") is SPEC
    assert registry.require("task.list") is SPEC
    assert registry.names() == ("task.list",)


def test_registry_rejects_duplicate_and_noncallable_implementation() -> None:
    registry = ToolRegistry()
    registry.register(SPEC, lambda arguments: [])
    with pytest.raises(ValidationError, match="already registered"):
        registry.register(SPEC, lambda arguments: [])
    other = ToolSpec(
        "task.get", "Get a local task.", {"type": "object", "properties": {}}, ("task.read",)
    )
    with pytest.raises(ValidationError, match="must be callable"):
        registry.register(other, 3)  # type: ignore[arg-type]


def test_registry_unknown_lookup_is_total_or_precise() -> None:
    registry = ToolRegistry()
    assert registry.get("missing") is None
    with pytest.raises(ValidationError, match="unknown tool") as captured:
        registry.require("missing")
    assert captured.value.context == {"path": "$.tool"}


def test_registry_unregister_removes_spec_and_callable_together() -> None:
    registry = ToolRegistry()
    registry.register(SPEC, lambda arguments: [])
    assert registry.unregister("task.list") is SPEC
    assert registry.names() == ()
    assert registry.get("task.list") is None
    with pytest.raises(ValidationError, match="unknown tool"):
        registry.unregister("task.list")
