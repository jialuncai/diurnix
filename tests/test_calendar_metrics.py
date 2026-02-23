from __future__ import annotations

from datetime import date

from diurnix.calendar_app import calendar_conflict_metrics
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_calendar_metrics_report_honest_planted_recall() -> None:
    entries = calendar_week_with_conflict(create_persona(10), 10, date(2026, 10, 26))
    metrics = calendar_conflict_metrics(entries)
    assert metrics["synthetic"] is True
    assert metrics["planted_conflict_count"] == 1
    assert metrics["recall"] == 1.0
    assert 0.0 <= metrics["precision"] <= 1.0


def test_calendar_metrics_define_empty_truth_recall() -> None:
    assert calendar_conflict_metrics(())["recall"] == 1.0
