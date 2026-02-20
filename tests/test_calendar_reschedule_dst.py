from __future__ import annotations

from dataclasses import replace
from datetime import date

from diurnix.calendar_app import propose_reschedule
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import generate_calendar_entry


def test_reschedule_uses_target_day_dst_offset() -> None:
    persona = replace(create_persona(2), timezone="America/New_York")
    source = generate_calendar_entry(persona, 2, 0, date(2026, 3, 6), hour=10)
    proposal = propose_reschedule(source, (), persona, date(2026, 3, 9))
    assert proposal is not None
    assert proposal.starts_at.isoformat().endswith("-04:00")


def test_reschedule_preserves_elapsed_duration_across_days() -> None:
    persona = replace(create_persona(2), timezone="America/New_York")
    source = generate_calendar_entry(persona, 2, 0, date(2026, 10, 30), hour=10)
    proposal = propose_reschedule(source, (), persona, date(2026, 11, 2))
    assert proposal is not None
    elapsed = int((proposal.ends_at.timestamp() - proposal.starts_at.timestamp()) // 60)
    assert elapsed == source.duration_minutes
