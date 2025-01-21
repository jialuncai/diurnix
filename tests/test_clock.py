from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.clock import SyntheticClock
from diurnix.errors import ValidationError

START = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_clock_advances_only_when_requested() -> None:
    clock = SyntheticClock(START)
    assert clock.now() == START
    assert clock.advance(timedelta(minutes=15)) == ()
    assert clock.now() == START + timedelta(minutes=15)


def test_due_timers_are_ordered_by_time_then_insertion() -> None:
    clock = SyntheticClock(START)
    clock.schedule("second", START + timedelta(minutes=10))
    clock.schedule("first-a", START + timedelta(minutes=5))
    clock.schedule("first-b", START + timedelta(minutes=5))
    due = clock.advance(timedelta(minutes=10))
    assert [timer.name for timer in due] == ["first-a", "first-b", "second"]
    assert clock.pending() == ()


def test_clock_rejects_naive_start_and_backward_travel() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        SyntheticClock(datetime(2026, 1, 1))
    clock = SyntheticClock(START)
    with pytest.raises(ValidationError, match="backward"):
        clock.advance(timedelta(microseconds=-1))


def test_clock_snapshot_restores_independent_pending_state() -> None:
    from diurnix.clock import restore_clock, snapshot_clock

    original = SyntheticClock(START)
    original.schedule("wake", START + timedelta(hours=1))
    restored = restore_clock(snapshot_clock(original))
    assert restored.pending() == original.pending()
    assert [timer.name for timer in restored.advance(timedelta(hours=1))] == ["wake"]
    assert len(original.pending()) == 1


def test_restored_clock_keeps_timer_tiebreak_sequence() -> None:
    from diurnix.clock import restore_clock, snapshot_clock

    original = SyntheticClock(START)
    original.schedule("before", START + timedelta(hours=1))
    restored = restore_clock(snapshot_clock(original))
    restored.schedule("after", START + timedelta(hours=1))
    assert [item.name for item in restored.advance(timedelta(hours=1))] == ["before", "after"]
