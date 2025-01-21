from __future__ import annotations

from datetime import date, datetime, time

import pytest

from diurnix.calendar import add_calendar_days, date_span, local_datetime, week_start
from diurnix.errors import ValidationError


def test_calendar_day_addition_preserves_wall_time_across_spring_dst() -> None:
    before = local_datetime(date(2026, 3, 7), time(9, 30), "America/New_York")
    after = add_calendar_days(before, 1)
    assert after.isoformat() == "2026-03-08T09:30:00-04:00"
    assert (after.timestamp() - before.timestamp()) / 3600 == 23


def test_ambiguous_fall_time_can_select_either_fold() -> None:
    first = local_datetime(date(2026, 11, 1), time(1, 30), "America/New_York", fold=0)
    second = local_datetime(date(2026, 11, 1), time(1, 30), "America/New_York", fold=1)
    assert first.utcoffset() != second.utcoffset()
    assert second.timestamp() - first.timestamp() == 3600


def test_nonexistent_spring_wall_time_is_rejected() -> None:
    with pytest.raises(ValidationError, match="does not exist"):
        local_datetime(date(2026, 3, 8), time(2, 30), "America/New_York")


def test_date_span_is_inclusive_and_week_start_is_configurable() -> None:
    assert date_span(date(2026, 10, 30), date(2026, 11, 1)) == (
        date(2026, 10, 30),
        date(2026, 10, 31),
        date(2026, 11, 1),
    )
    assert week_start(date(2026, 10, 30)) == date(2026, 10, 26)
    assert week_start(date(2026, 10, 30), first_weekday=6) == date(2026, 10, 25)


def test_calendar_rejects_unknown_timezone_and_invalid_fold() -> None:
    with pytest.raises(ValidationError, match="unknown IANA"):
        local_datetime(date(2026, 1, 1), time(8), "Mars/Olympus")
    with pytest.raises(ValidationError, match="fold"):
        local_datetime(date(2026, 1, 1), time(8), "UTC", fold=2)


def test_date_span_rejects_reverse_ranges() -> None:
    with pytest.raises(ValidationError, match="precedes"):
        date_span(date(2026, 2, 2), date(2026, 2, 1))


def test_week_start_rejects_out_of_range_weekday() -> None:
    for invalid in (-1, 7):
        with pytest.raises(ValidationError, match="zero to six"):
            week_start(date(2026, 1, 1), first_weekday=invalid)


def test_calendar_day_addition_rejects_naive_moment() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        add_calendar_days(datetime(2026, 1, 1, 8), 1)
