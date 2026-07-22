from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.habits_app import habit_heatmap_svg


def _event(event_id: str, local_date: str, status: HabitStatus, habit: str = "阅读"):
    return HabitCheckIn(event_id, datetime(2026, 1, 1, tzinfo=UTC), habit, local_date, status)


def test_habit_heatmap_maps_statuses_to_stable_colors() -> None:
    events = (
        _event("a", "2026-01-01", HabitStatus.DONE),
        _event("b", "2026-01-02", HabitStatus.SKIPPED),
        _event("c", "2026-01-03", HabitStatus.MISSED),
    )
    svg = habit_heatmap_svg(events)
    assert svg == habit_heatmap_svg(events)
    assert all(color in svg for color in ("#2f855a", "#d69e2e", "#c53030"))


def test_habit_heatmap_validates_cell_size() -> None:
    with pytest.raises(ValidationError, match="small"):
        habit_heatmap_svg((), cell_size=4)


def test_habit_heatmap_escapes_habit_names() -> None:
    svg = habit_heatmap_svg(
        (_event("x", "2026-01-01", HabitStatus.DONE, "<script>alert(1)</script>"),)
    )
    assert "<script>" not in svg and "&lt;script&gt;" in svg


def test_empty_habit_heatmap_is_valid_svg() -> None:
    svg = habit_heatmap_svg(())
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert svg.endswith("</svg>")
