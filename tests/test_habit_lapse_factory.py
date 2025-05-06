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
