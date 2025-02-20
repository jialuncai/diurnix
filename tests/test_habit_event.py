from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import EventKind, HabitCheckIn, HabitStatus

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def checkin(**changes: object) -> HabitCheckIn:
    values: dict[str, object] = {
        "event_id": "habit_1",
        "occurred_at": NOW,
        "habit": "walk",
        "local_date": "2026-10-30",
        "status": HabitStatus.DONE,
    }
    values.update(changes)
    return HabitCheckIn(**values)  # type: ignore[arg-type]


def test_habit_checkin_preserves_status_value_and_lapse_truth() -> None:
    event = checkin(value=30.5, planted_lapse=True)
    assert event.kind is EventKind.HABIT_CHECK_IN
    assert event.status is HabitStatus.DONE
    assert event.value == 30.5
    assert event.planted_lapse is True


def test_habit_checkin_rejects_bad_local_date() -> None:
    for value in ("2026-02-30", "30-10-2026", ""):
        with pytest.raises(ValidationError, match="ISO"):
            checkin(local_date=value)


def test_habit_checkin_rejects_nonfinite_optional_value() -> None:
    assert checkin(value=None).value is None
    for value in (float("nan"), float("inf")):
        with pytest.raises(ValidationError, match="finite"):
            checkin(value=value)


def test_habit_status_wire_values_are_stable() -> None:
    assert [item.value for item in HabitStatus] == ["done", "skipped", "missed"]
    assert {checkin(status=item).status for item in HabitStatus} == set(HabitStatus)


def test_habit_name_must_have_visible_content() -> None:
    with pytest.raises(ValidationError, match="habit name"):
        checkin(habit=" 	")


def test_valid_leap_day_is_accepted() -> None:
    assert checkin(local_date="2024-02-29").local_date == "2024-02-29"
