from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona, work_bounds


def test_work_bounds_return_local_aware_weekday_interval() -> None:
    persona = create_persona(0)
    bounds = work_bounds(persona, date(2026, 10, 30))
    assert bounds is not None
    start, end = bounds
    assert start.hour == 9 and end.hour == 18
    assert start.tzinfo is not None
    assert end.timestamp() - start.timestamp() == 9 * 3600


def test_work_bounds_omit_weekend_days() -> None:
    persona = create_persona(0)
    assert work_bounds(persona, date(2026, 10, 31)) is None
    assert work_bounds(persona, date(2026, 11, 1)) is None
