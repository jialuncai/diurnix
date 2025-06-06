"""Versioned portable codec for declarative tool registries."""

from __future__ import annotations

from typing import Any

from diurnix.errors import ValidationError
from diurnix.integrity import content_checksum
from diurnix.registry import ToolImplementation, ToolRegistry
from diurnix.tools import SideEffect, ToolSpec


def export_registry(registry: ToolRegistry) -> dict[str, Any]:
    """Export specs only; executable implementations never cross the wire."""
    tools = []
    for name in registry.names():
        spec = registry.require(name)
        tools.append(
            {
                "name": spec.name,
                "description": spec.description,
                "arguments": spec.arguments,
                "capabilities": list(spec.capabilities),
                "side_effect": spec.side_effect.value,
                "version": spec.version,
            }
        )
    return {"schema_version": 1, "tools": tools}


def import_registry(value: dict[str, Any], bindings: dict[str, ToolImplementation]) -> ToolRegistry:
    """Import strict specs while requiring an explicit local callable per name."""
    if set(value) != {"schema_version", "tools"} or value.get("schema_version") != 1:
        raise ValidationError("registry export does not match schema")
    registry = ToolRegistry()
    try:
        for item in value["tools"]:
            if set(item) != {
                "name",
                "description",
                "arguments",
                "capabilities",
                "side_effect",
                "version",
            }:
                raise ValidationError("tool export fields do not match schema")
            name = item["name"]
            if name not in bindings:
                raise ValidationError(f"missing tool binding: {name}")
            registry.register(
                ToolSpec(
                    name,
                    item["description"],
                    item["arguments"],
                    tuple(item["capabilities"]),
                    SideEffect(item["side_effect"]),
                    item["version"],
                ),
                bindings[name],
            )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid registry export payload") from error
    return registry


def registry_manifest(registry: ToolRegistry) -> dict[str, Any]:
    """Return versioned exported specs and their canonical checksum."""
    exported = export_registry(registry)
    return {
        "kind": "tool.registry",
        "schema_version": 1,
        "tool_count": len(exported["tools"]),
        "checksum": content_checksum(exported),
        "registry": exported,
    }
