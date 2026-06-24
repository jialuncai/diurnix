from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import detect_lapse_spans

START = datetime(2026, 1, 1, tzinfo=UTC)


def _event(index: int, status: HabitStatus):
    day = START.date() + timedelta(days=index)
    return HabitCheckIn(
        f"h-{index}", START + timedelta(days=index), "reading", day.isoformat(), status
    )


def test_lapse_detector_finds_consecutive_missed_run() -> None:
    events = tuple(
        _event(index, status)
        for index, status in enumerate(
            (
                HabitStatus.DONE,
                HabitStatus.MISSED,
                HabitStatus.MISSED,
                HabitStatus.MISSED,
                HabitStatus.DONE,
            )
        )
    )
    span = detect_lapse_spans(events)[0]
    assert span.starts_on == "2026-01-02" and span.ends_on == "2026-01-04"
    assert span.event_ids == ("h-1", "h-2", "h-3")


def test_lapse_detector_validates_minimum() -> None:
    with pytest.raises(ValidationError, match="positive"):
        detect_lapse_spans((), minimum_days=0)
