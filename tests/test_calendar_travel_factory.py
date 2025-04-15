from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import generate_calendar_week, with_travel_constraints


def test_travel_constraints_are_seeded_and_location_aware() -> None:
    entries = generate_calendar_week(create_persona(3), 8, date(2026, 10, 26))
    first = with_travel_constraints(entries, 19)
    second = with_travel_constraints(entries, 19)
    assert first == second
    assert all(entry.travel_minutes == 0 for entry in first if entry.location == "home")
    assert all(entry.travel_minutes > 0 for entry in first if entry.location != "home")


def test_travel_constraint_copy_preserves_source_events() -> None:
    entries = generate_calendar_week(create_persona(3), 8, date(2026, 10, 26))
    constrained = with_travel_constraints(entries, 19)
    assert [entry.event_id for entry in constrained] == [entry.event_id for entry in entries]
    assert all(entry.travel_minutes == 0 for entry in entries)
