from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.calendar_app import find_travel_conflicts
from diurnix.events import CalendarEntry

BASE = datetime(2026, 1, 1, 9, tzinfo=UTC)


def _entry(event_id: str, start: int, end: int, location: str, travel: int):
    return CalendarEntry(
        event_id,
        BASE + timedelta(minutes=start),
        event_id,
        BASE + timedelta(minutes=start),
        BASE + timedelta(minutes=end),
        location,
        travel,
    )


def test_travel_conflict_reports_missing_buffer_minutes() -> None:
    left = _entry("a", 0, 30, "home", 0)
    right = _entry("b", 40, 70, "campus", 20)
    assert find_travel_conflicts((right, left)) == ((left, right, 10),)


def test_same_location_and_sufficient_buffer_are_safe() -> None:
    left = _entry("a", 0, 30, "campus", 20)
    same = _entry("b", 30, 60, "campus", 20)
    later = _entry("c", 90, 120, "home", 20)
    assert find_travel_conflicts((left, same, later)) == ()
