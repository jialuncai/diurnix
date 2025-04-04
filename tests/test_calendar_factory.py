from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import generate_calendar_entry


def test_calendar_entry_factory_is_seeded_and_local() -> None:
    persona = create_persona(3)
    first = generate_calendar_entry(persona, 8, 0, date(2026, 10, 30))
    second = generate_calendar_entry(persona, 8, 0, date(2026, 10, 30))
    assert first == second
    assert first.starts_at.hour == 10
    assert first.starts_at.tzinfo is not None
    assert first.duration_minutes in {30, 45, 60, 90}


def test_calendar_entry_index_changes_identity_and_content_stream() -> None:
    persona = create_persona(3)
    entries = [generate_calendar_entry(persona, 8, index, date(2026, 10, 30)) for index in range(8)]
    assert len({entry.event_id for entry in entries}) == 8
    assert len({(entry.title, entry.location, entry.duration_minutes) for entry in entries}) > 1
