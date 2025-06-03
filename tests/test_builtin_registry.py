from __future__ import annotations

from datetime import UTC, datetime

from diurnix.builtin_tools import default_registry
from diurnix.clock import SyntheticClock


def test_default_registry_is_fresh_and_complete() -> None:
    clock = SyntheticClock(datetime(2026, 10, 30, 8, tzinfo=UTC))
    first = default_registry(clock)
    second = default_registry(clock)
    assert first is not second
    assert first.names() == ("clock.advance", "clock.now", "model.loopback")
    first.unregister("clock.now")
    assert "clock.now" in second.names()


def test_default_registry_capabilities_are_queryable() -> None:
    registry = default_registry(SyntheticClock(datetime(2026, 10, 30, 8, tzinfo=UTC)))
    assert [item.name for item in registry.by_capability("clock.read,model.mock")] == [
        "clock.now",
        "model.loopback",
    ]
