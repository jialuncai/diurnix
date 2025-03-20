from __future__ import annotations

from datetime import time

import pytest

from diurnix.errors import ValidationError
from diurnix.persona import WorkHours


def test_work_hours_use_half_open_boundaries() -> None:
    hours = WorkHours(time(9), time(17, 30))
    assert hours.contains(0, time(9))
    assert hours.contains(4, time(17, 29, 59))
    assert not hours.contains(4, time(17, 30))
    assert not hours.contains(5, time(12))


def test_work_hours_reject_nonpositive_window() -> None:
    for start, end in ((time(9), time(9)), (time(18), time(9))):
        with pytest.raises(ValidationError, match="positive"):
            WorkHours(start, end)


def test_work_hours_validate_weekday_set() -> None:
    for weekdays in ((), (1, 1), (-1,), (7,)):
        with pytest.raises(ValidationError, match="weekdays"):
            WorkHours(time(9), time(17), weekdays)


def test_work_hours_support_weekend_and_split_week_patterns() -> None:
    weekend = WorkHours(time(8), time(12), (5, 6))
    assert weekend.contains(5, time(10))
    assert weekend.contains(6, time(10))
    assert not weekend.contains(0, time(10))
    split = WorkHours(time(10), time(16), (0, 2, 4))
    assert [split.contains(day, time(12)) for day in range(5)] == [True, False, True, False, True]


def test_work_hours_are_immutable() -> None:
    from dataclasses import FrozenInstanceError

    hours = WorkHours(time(9), time(17))
    with pytest.raises(FrozenInstanceError):
        hours.weekdays = (0,)  # type: ignore[misc]
