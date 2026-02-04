from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.calendar_app import IntervalRelation, interval_relation
from diurnix.events import CalendarEntry

BASE = datetime(2026, 1, 1, tzinfo=UTC)


def _entry(event_id: str, start: int, end: int):
    return CalendarEntry(
        event_id,
        BASE + timedelta(minutes=start),
        event_id,
        BASE + timedelta(minutes=start),
        BASE + timedelta(minutes=end),
    )


def test_interval_relation_distinguishes_disjoint_and_touching() -> None:
    anchor = _entry("a", 10, 20)
    assert interval_relation(anchor, _entry("before", 30, 40)) is IntervalRelation.BEFORE
    assert interval_relation(anchor, _entry("meets", 20, 30)) is IntervalRelation.MEETS
    assert interval_relation(anchor, _entry("after", 0, 5)) is IntervalRelation.AFTER


def test_interval_relation_distinguishes_equal_and_containment() -> None:
    anchor = _entry("a", 10, 30)
    assert interval_relation(anchor, _entry("same", 10, 30)) is IntervalRelation.EQUALS
    assert interval_relation(anchor, _entry("inner", 15, 25)) is IntervalRelation.CONTAINS
    assert interval_relation(_entry("inner", 15, 25), anchor) is IntervalRelation.DURING
