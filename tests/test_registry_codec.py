from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.registry_codec import export_registry
from diurnix.tools import SideEffect, ToolSpec


def sample_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "mail.send",
            "Send synthetic mail.",
            {"type": "object", "properties": {"text": {"type": "string"}}},
            ("mail.send",),
            SideEffect.EXTERNAL,
            2,
        ),
        lambda arguments: arguments,
    )
    return registry


def test_registry_export_contains_specs_but_not_callables() -> None:
    exported = export_registry(sample_registry())
    assert exported == {
        "schema_version": 1,
        "tools": [
            {
                "name": "mail.send",
                "description": "Send synthetic mail.",
                "arguments": {"type": "object", "properties": {"text": {"type": "string"}}},
                "capabilities": ["mail.send"],
                "side_effect": "external",
                "version": 2,
            }
        ],
    }
