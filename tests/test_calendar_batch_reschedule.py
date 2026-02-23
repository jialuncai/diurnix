from __future__ import annotations

from datetime import date

from diurnix.calendar_app import propose_conflict_resolutions
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_batch_reschedule_covers_planted_conflicts() -> None:
    persona = create_persona(13)
    entries = calendar_week_with_conflict(persona, 13, date(2026, 10, 26))
    proposals = propose_conflict_resolutions(entries, persona)
    planted = {entry.event_id for entry in entries if entry.planted_conflict}
    assert {proposal.entry_id for proposal in proposals} == planted


def test_batch_reschedule_is_stable_for_input_order() -> None:
    persona = create_persona(13)
    entries = calendar_week_with_conflict(persona, 13, date(2026, 10, 26))
    assert propose_conflict_resolutions(entries, persona) == propose_conflict_resolutions(
        tuple(reversed(entries)), persona
    )
