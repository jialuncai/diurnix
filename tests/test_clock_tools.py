from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.builtin_tools import register_clock_tools
from diurnix.clock import SyntheticClock
from diurnix.registry import ToolRegistry


def test_clock_tools_read_advance_and_return_due_names() -> None:
    start = datetime(2026, 10, 30, 8, tzinfo=UTC)
    clock = SyntheticClock(start)
    clock.schedule("wake", start + timedelta(seconds=5))
    registry = ToolRegistry()
    register_clock_tools(registry, clock)
    assert registry.invoke("clock.now", {}) == {"now": start.isoformat()}
    assert registry.invoke("clock.advance", {"seconds": 5}) == {
        "now": (start + timedelta(seconds=5)).isoformat(),
        "due": ["wake"],
    }


def test_clock_advance_tool_rejects_negative_duration() -> None:
    import pytest

    from diurnix.errors import ValidationError

    registry = ToolRegistry()
    register_clock_tools(registry, SyntheticClock(datetime(2026, 10, 30, 8, tzinfo=UTC)))
    with pytest.raises(ValidationError, match="below minimum"):
        registry.invoke("clock.advance", {"seconds": -1})
