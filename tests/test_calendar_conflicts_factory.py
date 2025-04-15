from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_calendar_conflict_factory_plants_one_labeled_overlap() -> None:
    entries = calendar_week_with_conflict(create_persona(3), 8, date(2026, 10, 26))
    planted = [entry for entry in entries if entry.planted_conflict]
    assert len(planted) == 1
    conflict = planted[0]
    overlapping = [
        entry
        for entry in entries
        if entry is not conflict
        and entry.starts_at < conflict.ends_at
        and conflict.starts_at < entry.ends_at
    ]
    assert len(overlapping) == 1


def test_calendar_conflict_stream_is_chronologically_ordered() -> None:
    entries = calendar_week_with_conflict(create_persona(3), 8, date(2026, 10, 26))
    assert list(entries) == sorted(entries, key=lambda entry: (entry.starts_at, entry.event_id))
