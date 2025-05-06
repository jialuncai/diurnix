from __future__ import annotations

from datetime import date

import pytest

from diurnix.errors import ValidationError
from diurnix.events import HabitStatus
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_stream, plant_habit_lapse


def test_planted_lapse_marks_exact_habit_date_range() -> None:
    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    habit = persona.habit_goals[0].name
    planted = plant_habit_lapse(events, habit, date(2026, 10, 10), days=3)
    lapses = [item for item in planted if item.planted_lapse]
    assert [item.local_date for item in lapses] == ["2026-10-10", "2026-10-11", "2026-10-12"]
    assert all(item.habit == habit and item.status is HabitStatus.MISSED for item in lapses)


def test_lapse_planting_requires_positive_duration() -> None:
    with pytest.raises(ValidationError, match="positive"):
        plant_habit_lapse((), "walk", date(2026, 10, 1), days=0)


def test_grace_skip_converts_only_ordinary_miss() -> None:
    from diurnix.synthetic_habits import mark_grace_skip

    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    missed = next(item for item in events if item.status is HabitStatus.MISSED)
    skipped = mark_grace_skip(missed)
    assert skipped.event_id == missed.event_id
    assert skipped.status is HabitStatus.SKIPPED
    assert skipped.planted_lapse is False


def test_grace_skip_rejects_done_and_planted_lapse() -> None:
    from diurnix.synthetic_habits import mark_grace_skip

    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    done = next(item for item in events if item.status is HabitStatus.DONE)
    with pytest.raises(ValidationError, match="ordinary missed"):
        mark_grace_skip(done)
    lapse = plant_habit_lapse(events, persona.habit_goals[0].name, date(2026, 10, 2))[1]
    if lapse.planted_lapse:
        with pytest.raises(ValidationError, match="ordinary missed"):
            mark_grace_skip(lapse)
