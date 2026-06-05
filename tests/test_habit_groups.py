from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import group_habit_checkins


def _event(event_id: str, habit: str, local_date: str):
    return HabitCheckIn(
        event_id, datetime(2026, 1, 1, tzinfo=UTC), habit, local_date, HabitStatus.DONE
    )


def test_habit_groups_sort_names_and_local_dates() -> None:
    events = (
        _event("b2", "阅读", "2026-01-02"),
        _event("a", "步行", "2026-01-01"),
        _event("b1", "阅读", "2026-01-01"),
    )
    grouped = group_habit_checkins(events)
    assert tuple(grouped) == ("步行", "阅读")
    assert tuple(item.event_id for item in grouped["阅读"]) == ("b1", "b2")


def test_habit_groups_reject_duplicate_local_day() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        group_habit_checkins((_event("a", "阅读", "2026-01-01"), _event("b", "阅读", "2026-01-01")))
