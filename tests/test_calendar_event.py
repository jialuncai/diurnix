from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import CalendarEntry, EventKind

START = datetime(2026, 10, 30, 9, tzinfo=UTC)


def entry(**changes: object) -> CalendarEntry:
    values: dict[str, object] = {
        "event_id": "calendar_1",
        "occurred_at": START,
        "title": "Synthetic planning",
        "starts_at": START,
        "ends_at": START + timedelta(minutes=45),
    }
    values.update(changes)
    return CalendarEntry(**values)  # type: ignore[arg-type]


def test_calendar_entry_reports_elapsed_duration_and_kind() -> None:
    event = entry(travel_minutes=15, planted_conflict=True)
    assert event.kind is EventKind.CALENDAR_ENTRY
    assert event.duration_minutes == 45
    assert event.travel_minutes == 15
    assert event.planted_conflict is True


def test_calendar_entry_requires_positive_interval() -> None:
    for end in (START, START - timedelta(microseconds=1)):
        with pytest.raises(ValidationError, match="positive duration"):
            entry(ends_at=end)


def test_calendar_entry_rejects_blank_title_and_negative_travel() -> None:
    with pytest.raises(ValidationError, match="title"):
        entry(title=" ")
    with pytest.raises(ValidationError, match="travel"):
        entry(travel_minutes=-1)


def test_calendar_entry_rejects_naive_interval_boundaries() -> None:
    naive = datetime(2026, 10, 30, 9)
    with pytest.raises(ValidationError, match="timezone-aware") as start_error:
        entry(starts_at=naive)
    assert start_error.value.context == {"path": "$.starts_at"}
    with pytest.raises(ValidationError, match="timezone-aware") as end_error:
        entry(ends_at=naive)
    assert end_error.value.context == {"path": "$.ends_at"}


def test_calendar_elapsed_duration_handles_offset_transition() -> None:
    from datetime import date, time

    from diurnix.calendar import local_datetime

    start = local_datetime(date(2026, 11, 1), time(1, 30), "America/New_York", fold=0)
    end = local_datetime(date(2026, 11, 1), time(1, 30), "America/New_York", fold=1)
    assert entry(starts_at=start, ends_at=end).duration_minutes == 60
