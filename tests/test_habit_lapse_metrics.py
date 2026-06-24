from __future__ import annotations

from datetime import date

from diurnix.habits_app import detect_lapse_spans, lapse_recovery_metrics
from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import generate_habit_stream, plant_habit_lapse


def _events():
    persona = create_persona(4)
    events = generate_habit_stream(persona, 4, date(2026, 1, 1), days=14)
    return plant_habit_lapse(events, persona.habit_goals[0].name, date(2026, 1, 5), days=3)


def test_lapse_metrics_report_planted_recall() -> None:
    events = _events()
    metrics = lapse_recovery_metrics(events, detect_lapse_spans(events))
    assert metrics["synthetic"] is True and metrics["planted_count"] == 3
    assert metrics["recall"] == 1.0
    assert 0.0 <= metrics["precision"] <= 1.0


def test_empty_lapse_truth_has_defined_recall() -> None:
    assert lapse_recovery_metrics((), ())["recall"] == 1.0


def test_seeded_lapse_metrics_are_reproducible() -> None:
    events = _events()
    spans = detect_lapse_spans(events)
    assert lapse_recovery_metrics(events, spans) == lapse_recovery_metrics(events, spans)


def test_detected_lapse_spans_are_chronological() -> None:
    spans = detect_lapse_spans(_events())
    assert tuple((span.habit, span.starts_on) for span in spans) == tuple(
        sorted((span.habit, span.starts_on) for span in spans)
    )
