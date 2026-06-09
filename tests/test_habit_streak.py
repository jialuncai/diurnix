from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import calculate_streak

START = datetime(2026, 1, 1, tzinfo=UTC)


def _event(index: int, status: HabitStatus):
    day = START.date() + timedelta(days=index)
    return HabitCheckIn(
        f"h-{index}", START + timedelta(days=index), "阅读", day.isoformat(), status
    )


def test_streak_tracks_current_and_longest_runs() -> None:
    events = tuple(
        _event(index, status)
        for index, status in enumerate(
            (
                HabitStatus.DONE,
                HabitStatus.DONE,
                HabitStatus.MISSED,
                HabitStatus.DONE,
                HabitStatus.DONE,
                HabitStatus.DONE,
            )
        )
    )
    assert calculate_streak(events) == type(calculate_streak(events))("阅读", 3, 3, 5, 0)


def test_empty_streak_has_explicit_zero_summary() -> None:
    summary = calculate_streak(())
    assert summary.current == 0 and summary.longest == 0 and summary.habit == ""
