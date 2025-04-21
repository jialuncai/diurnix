from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import generate_calendar_entry, generate_calendar_week


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


def test_calendar_week_uses_only_persona_workdays() -> None:
    from diurnix.synthetic_calendar import generate_calendar_week

    persona = create_persona(3)
    entries = generate_calendar_week(persona, 8, date(2026, 10, 26))
    assert len(entries) == 10
    assert {entry.starts_at.weekday() for entry in entries} == {0, 1, 2, 3, 4}
    assert [entry.starts_at.hour for entry in entries] == [10, 14] * 5


def test_calendar_week_handles_non_monday_start_without_duplication() -> None:
    from diurnix.synthetic_calendar import generate_calendar_week

    entries = generate_calendar_week(create_persona(3), 8, date(2026, 10, 30))
    assert len(entries) == 10
    assert len({entry.event_id for entry in entries}) == 10


def test_calendar_week_preserves_wall_slots_across_fall_dst() -> None:
    persona = create_persona(4)
    assert persona.timezone == "America/New_York"
    entries = generate_calendar_week(persona, 8, date(2026, 10, 30))
    assert {entry.starts_at.hour for entry in entries} == {10, 14}
    before = next(entry for entry in entries if entry.starts_at.date() == date(2026, 10, 30))
    after = next(entry for entry in entries if entry.starts_at.date() == date(2026, 11, 2))
    assert before.starts_at.utcoffset() != after.starts_at.utcoffset()


def test_calendar_factory_elapsed_durations_remain_allowed_across_dst() -> None:
    persona = create_persona(4)
    entries = generate_calendar_week(persona, 8, date(2026, 10, 30))
    assert {entry.duration_minutes for entry in entries} <= {30, 45, 60, 90}
