"""Deterministic in-process tools used by offline applications and tests."""

from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def register_loopback_tool(registry: ToolRegistry) -> None:
    """Register a mock model adapter that returns scripted text literally."""
    registry.register(
        ToolSpec(
            "model.loopback",
            "Return scripted offline adapter text.",
            {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
            ("model.mock",),
        ),
        lambda arguments: {"text": arguments["text"], "adapter": "loopback"},
    )
