from __future__ import annotations

from datetime import date

from diurnix.calendar_app import find_calendar_conflicts
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_conflict_detector_recovers_planted_overlap() -> None:
    entries = calendar_week_with_conflict(create_persona(3), 3, date(2026, 10, 26))
    pairs = find_calendar_conflicts(entries)
    detected_ids = {entry.event_id for pair in pairs for entry in pair}
    planted_ids = {entry.event_id for entry in entries if entry.planted_conflict}
    assert planted_ids and planted_ids <= detected_ids


def test_nonoverlapping_calendar_has_no_conflicts() -> None:
    entries = calendar_week_with_conflict(create_persona(3), 3, date(2026, 10, 26))
    clean = tuple(entry for entry in entries if not entry.planted_conflict)
    assert find_calendar_conflicts(clean) == ()
