from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.persona import HabitGoal


def test_habit_goal_accepts_inclusive_bounds() -> None:
    assert HabitGoal("daily", 7, 23, 3).target_days_per_week == 7
    assert HabitGoal("weekly", 1, 0, 0).preferred_hour == 0


def test_habit_goal_validates_all_ranges_together() -> None:
    for kwargs, match in (
        ({"target_days_per_week": 0}, "target days"),
        ({"target_days_per_week": 8}, "target days"),
        ({"preferred_hour": -1}, "preferred hour"),
        ({"preferred_hour": 24}, "preferred hour"),
        ({"grace_days": 4}, "grace days"),
    ):
        values = {"name": "walk", "target_days_per_week": 5, "preferred_hour": 8}
        values.update(kwargs)
        with pytest.raises(ValidationError, match=match):
            HabitGoal(**values)


def test_habit_goal_rejects_blank_name() -> None:
    with pytest.raises(ValidationError, match="name"):
        HabitGoal(" ", 3, 8)
