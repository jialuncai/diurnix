from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def test_registry_clone_has_independent_membership() -> None:
    registry = ToolRegistry()
    spec = ToolSpec("sample", "Sample.", {"type": "object", "properties": {}}, ("sample.read",))
    registry.register(spec, lambda arguments: "ok")
    cloned = registry.clone()
    assert cloned.names() == registry.names()
    assert cloned.invoke("sample", {}) == "ok"
    cloned.unregister("sample")
    assert registry.names() == ("sample",)


def test_empty_registry_clone_is_empty_and_distinct() -> None:
    registry = ToolRegistry()
    cloned = registry.clone()
    assert cloned is not registry
    assert cloned.names() == ()
