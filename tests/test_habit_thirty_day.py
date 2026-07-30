from __future__ import annotations

from datetime import date

from diurnix.habits_app import (
    detect_lapse_spans,
    habit_analysis_manifest,
    habit_consistency_report,
    lapse_recovery_metrics,
)
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_stream, plant_habit_lapse


def _run(seed: int):
    start = date(2026, 1, 1)
    persona = create_persona(seed)
    events = generate_habit_stream(persona, seed, start, days=30)
    events = plant_habit_lapse(events, persona.habit_goals[0].name, start, days=3)
    report = habit_consistency_report(events, persona.habit_goals)
    metrics = lapse_recovery_metrics(events, detect_lapse_spans(events))
    return report, metrics, habit_analysis_manifest(events, report, seed)


def test_thirty_day_habit_analysis_is_byte_fact_stable() -> None:
    assert _run(21) == _run(21)


def test_thirty_day_analysis_recovers_planted_lapse() -> None:
    report, metrics, manifest = _run(21)
    assert report["habit_count"] == 2
    assert metrics["planted_count"] == 3 and metrics["recall"] == 1.0
    assert manifest["metrics"] == metrics
