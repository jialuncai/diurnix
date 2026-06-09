from __future__ import annotations

from datetime import date, time, timedelta

from diurnix.calendar import local_datetime
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import calculate_streak


def _event(index: int, day: date):
    occurred = local_datetime(day, time(8), "America/New_York")
    return HabitCheckIn(f"h-{index}", occurred, "walk", day.isoformat(), HabitStatus.DONE)


def test_spring_forward_23_hour_day_keeps_streak() -> None:
    start = date(2026, 3, 7)
    events = tuple(_event(index, start + timedelta(days=index)) for index in range(3))
    assert calculate_streak(events).current == 3
    assert (events[1].occurred_at.timestamp() - events[0].occurred_at.timestamp()) / 3600 == 23
    assert (events[2].occurred_at.timestamp() - events[1].occurred_at.timestamp()) / 3600 == 24


def test_fall_back_25_hour_day_keeps_streak() -> None:
    start = date(2026, 10, 31)
    events = tuple(_event(index, start + timedelta(days=index)) for index in range(3))
    assert calculate_streak(events).current == 3
    assert (events[1].occurred_at.timestamp() - events[0].occurred_at.timestamp()) / 3600 == 25
