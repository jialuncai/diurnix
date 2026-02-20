from __future__ import annotations

from datetime import date

import pytest

from diurnix.calendar_app import propose_reschedule
from diurnix.errors import ValidationError
from diurnix.persona_factory import create_persona, work_bounds
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_reschedule_proposal_stays_in_work_hours() -> None:
    persona = create_persona(4)
    day = date(2026, 10, 26)
    entries = calendar_week_with_conflict(persona, 4, day)
    conflicted = next(entry for entry in entries if entry.planted_conflict)
    proposal = propose_reschedule(conflicted, entries, persona, day)
    assert proposal is not None
    start, end = work_bounds(persona, day)
    assert start <= proposal.starts_at < proposal.ends_at <= end


def test_reschedule_validates_search_step() -> None:
    persona = create_persona(4)
    day = date(2026, 10, 26)
    entry = calendar_week_with_conflict(persona, 4, day)[0]
    with pytest.raises(ValidationError, match="positive"):
        propose_reschedule(entry, (), persona, day, step_minutes=0)


def test_reschedule_returns_none_on_persona_day_off() -> None:
    persona = create_persona(4)
    monday = date(2026, 10, 26)
    entry = calendar_week_with_conflict(persona, 4, monday)[0]
    assert propose_reschedule(entry, (), persona, date(2026, 11, 1)) is None


def test_reschedule_returns_none_when_workday_is_full() -> None:
    from diurnix.events import CalendarEntry

    persona = create_persona(4)
    day = date(2026, 10, 26)
    start, end = work_bounds(persona, day)
    source = calendar_week_with_conflict(persona, 4, day)[0]
    blocker = CalendarEntry("blocker", start, "full day", start, end, "home")
    assert propose_reschedule(source, (blocker,), persona, day) is None
