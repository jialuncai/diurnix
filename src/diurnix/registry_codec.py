"""Versioned portable codec for declarative tool registries."""

from __future__ import annotations

from typing import Any

from diurnix.registry import ToolRegistry


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
