from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.registry_codec import diff_registries
from diurnix.tools import ToolSpec


def add(registry: ToolRegistry, name: str, version: int = 1) -> None:
    registry.register(
        ToolSpec(
            name,
            f"Tool {name}.",
            {"type": "object", "properties": {}},
            ("sample.read",),
            version=version,
        ),
        lambda arguments: None,
    )


def test_registry_diff_separates_added_removed_and_changed() -> None:
    before, after = ToolRegistry(), ToolRegistry()
    add(before, "removed")
    add(before, "changed", 1)
    add(after, "added")
    add(after, "changed", 2)
    assert diff_registries(before, after) == {
        "added": ("added",),
        "removed": ("removed",),
        "changed": ("changed",),
    }


def test_registry_diff_ignores_callable_identity() -> None:
    registry = ToolRegistry()
    add(registry, "same")
    assert diff_registries(registry, registry.clone()) == {
        "added": (),
        "removed": (),
        "changed": (),
    }
