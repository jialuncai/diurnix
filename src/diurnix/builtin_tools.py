"""Deterministic in-process tools used by offline applications and tests."""

from __future__ import annotations

from typing import Any

from diurnix.clock import SyntheticClock
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


def register_clock_tools(registry: ToolRegistry, clock: SyntheticClock) -> None:
    """Register read and bounded advance operations for a synthetic clock."""
    registry.register(
        ToolSpec(
            "clock.now",
            "Read synthetic time.",
            {"type": "object", "properties": {}},
            ("clock.read",),
        ),
        lambda arguments: {"now": clock.now().isoformat()},
    )
    registry.register(
        ToolSpec(
            "clock.advance",
            "Advance synthetic time.",
            {
                "type": "object",
                "properties": {"seconds": {"type": "number", "minimum": 0}},
                "required": ["seconds"],
                "additionalProperties": False,
            },
            ("clock.write",),
        ),
        lambda arguments: _advance_clock(clock, float(arguments["seconds"])),
    )


def _advance_clock(clock: SyntheticClock, seconds: float) -> dict[str, Any]:
    from datetime import timedelta

    due = clock.advance(timedelta(seconds=seconds))
    return {"now": clock.now().isoformat(), "due": [timer.name for timer in due]}
