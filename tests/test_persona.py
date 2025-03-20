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
