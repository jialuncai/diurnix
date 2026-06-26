from __future__ import annotations

from datetime import date

from diurnix.habits_app import schedule_routine
from diurnix.persona import HabitGoal


def test_routine_after_spring_transition_uses_new_offset() -> None:
    schedule = schedule_routine(HabitGoal("walk", 5, 8), date(2026, 3, 9), (), "America/New_York")
    assert schedule is not None and schedule.starts_at.isoformat().endswith("-04:00")


def test_routine_after_fall_transition_uses_standard_offset() -> None:
    schedule = schedule_routine(HabitGoal("walk", 5, 8), date(2026, 11, 2), (), "America/New_York")
    assert schedule is not None and schedule.starts_at.isoformat().endswith("-05:00")
