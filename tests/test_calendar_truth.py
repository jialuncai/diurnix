from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import (
    calendar_ground_truth,
    calendar_week_with_conflict,
    with_travel_constraints,
)


def test_calendar_truth_identifies_planted_records() -> None:
    entries = calendar_week_with_conflict(create_persona(3), 8, date(2026, 10, 26))
    entries = with_travel_constraints(entries, 19)
    truth = calendar_ground_truth(entries)
    assert truth["entry_count"] == len(entries)
    assert truth["conflict_ids"] == [entry.event_id for entry in entries if entry.planted_conflict]
    assert truth["travel_minutes"] == {entry.event_id: entry.travel_minutes for entry in entries}
