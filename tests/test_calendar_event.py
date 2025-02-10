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
