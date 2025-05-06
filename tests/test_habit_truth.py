from __future__ import annotations

from datetime import date

from diurnix.events import HabitStatus
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_stream, habit_ground_truth, plant_habit_lapse


def test_habit_truth_identifies_exact_planted_lapses() -> None:
    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    events = plant_habit_lapse(events, persona.habit_goals[0].name, date(2026, 10, 10))
    truth = habit_ground_truth(events)
    assert truth["checkin_count"] == len(events)
    assert truth["lapse_ids"] == [item.event_id for item in events if item.planted_lapse]
    assert list(truth["status_counts"]) == [status.value for status in HabitStatus]
    assert sum(truth["status_counts"].values()) == len(events)


def test_empty_habit_truth_retains_status_schema() -> None:
    assert habit_ground_truth(())["status_counts"] == {status.value: 0 for status in HabitStatus}


def test_lapse_span_recovers_planted_bounds_and_length() -> None:
    from diurnix.synthetic_habits import planted_lapse_spans

    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    habit = persona.habit_goals[0].name
    events = plant_habit_lapse(events, habit, date(2026, 10, 10), days=4)
    assert planted_lapse_spans(events) == {habit: ("2026-10-10", "2026-10-13", 4)}
    assert planted_lapse_spans(()) == {}
