from __future__ import annotations

from datetime import date, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import CalendarEntry
from diurnix.habits_app import schedule_routine
from diurnix.persona import HabitGoal

DAY = date(2026, 10, 30)
GOAL = HabitGoal("阅读", 5, 8, 1)


def test_routine_schedule_moves_after_calendar_conflict() -> None:
    preferred = schedule_routine(GOAL, DAY, (), "Asia/Shanghai")
    assert preferred is not None
    blocker = CalendarEntry(
        "blocker",
        preferred.starts_at,
        "meeting",
        preferred.starts_at,
        preferred.ends_at + timedelta(minutes=10),
    )
    moved = schedule_routine(GOAL, DAY, (blocker,), "Asia/Shanghai")
    assert moved is not None and moved.starts_at >= blocker.ends_at


def test_routine_schedule_validates_duration() -> None:
    with pytest.raises(ValidationError, match="bounds"):
        schedule_routine(GOAL, DAY, (), "Asia/Shanghai", duration_minutes=0)
