from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import calculate_streak

START = datetime(2026, 1, 1, tzinfo=UTC)


def _event(index: int, status: HabitStatus):
    day = START.date() + timedelta(days=index)
    return HabitCheckIn(
        f"h-{index}", START + timedelta(days=index), "reading", day.isoformat(), status
    )


def test_one_grace_skip_preserves_streak() -> None:
    events = (
        _event(0, HabitStatus.DONE),
        _event(1, HabitStatus.SKIPPED),
        _event(2, HabitStatus.DONE),
    )
    summary = calculate_streak(events, grace_days=1)
    assert summary.current == 3 and summary.grace_days_used == 1


def test_skip_without_grace_breaks_streak() -> None:
    events = (
        _event(0, HabitStatus.DONE),
        _event(1, HabitStatus.SKIPPED),
        _event(2, HabitStatus.DONE),
    )
    assert calculate_streak(events).current == 1


def test_second_skip_beyond_grace_resets_streak() -> None:
    events = (
        _event(0, HabitStatus.DONE),
        _event(1, HabitStatus.SKIPPED),
        _event(2, HabitStatus.SKIPPED),
        _event(3, HabitStatus.DONE),
    )
    summary = calculate_streak(events, grace_days=1)
    assert summary.current == 1 and summary.longest == 2


def test_grace_budget_resets_after_a_real_break() -> None:
    events = (
        _event(0, HabitStatus.SKIPPED),
        _event(1, HabitStatus.MISSED),
        _event(2, HabitStatus.SKIPPED),
        _event(3, HabitStatus.DONE),
    )
    summary = calculate_streak(events, grace_days=1)
    assert summary.current == 2 and summary.grace_days_used == 2
