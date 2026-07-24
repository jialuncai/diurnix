from __future__ import annotations

from datetime import date

from diurnix.habits_app import habit_consistency_report
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_stream


def test_habit_report_covers_every_persona_goal() -> None:
    persona = create_persona(5)
    events = generate_habit_stream(persona, 5, date(2026, 1, 1), days=14)
    report = habit_consistency_report(events, persona.habit_goals)
    assert report["habit_count"] == len(persona.habit_goals)
    assert [row["habit"] for row in report["habits"]] == [goal.name for goal in persona.habit_goals]
    assert all(0.0 <= row["consistency"] <= 1.0 for row in report["habits"])


def test_empty_goal_report_is_explicit() -> None:
    assert habit_consistency_report((), ()) == {"habit_count": 0, "habits": [], "synthetic": True}
