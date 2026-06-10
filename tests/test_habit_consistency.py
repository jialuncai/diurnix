from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import habit_consistency

START = datetime(2026, 1, 1, tzinfo=UTC)


def _events(done_days: set[int]):
    return tuple(
        HabitCheckIn(
            f"h-{index}",
            START + timedelta(days=index),
            "reading",
            (START.date() + timedelta(days=index)).isoformat(),
            HabitStatus.DONE if index in done_days else HabitStatus.MISSED,
        )
        for index in range(7)
    )


def test_consistency_meets_weekly_target_at_one() -> None:
    assert habit_consistency(_events({0, 1, 2, 3, 4}), 5) == 1.0
    assert habit_consistency(_events({0, 1, 2}), 5) == 0.6


def test_consistency_validates_target() -> None:
    with pytest.raises(ValidationError, match="one to seven"):
        habit_consistency((), 0)
