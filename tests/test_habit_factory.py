from __future__ import annotations

from datetime import date

from diurnix.events import HabitStatus
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_checkin


def test_habit_checkin_factory_is_seeded_and_local() -> None:
    persona = create_persona(3)
    goal = persona.habit_goals[0]
    first = generate_habit_checkin(persona, goal, 6, 0, date(2026, 10, 1))
    assert first == generate_habit_checkin(persona, goal, 6, 0, date(2026, 10, 1))
    assert first.local_date == "2026-10-01"
    assert first.occurred_at.hour == goal.preferred_hour
    assert first.status in (HabitStatus.DONE, HabitStatus.MISSED)
    assert first.value in (0.0, 1.0)


def test_habit_completion_value_matches_status() -> None:
    persona = create_persona(3)
    goal = persona.habit_goals[0]
    for index in range(50):
        item = generate_habit_checkin(persona, goal, 6, index, date(2026, 10, 1))
        assert (item.status is HabitStatus.DONE) is (item.value == 1.0)
