from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from diurnix.tasks_app import (
    DailyTaskPlan,
    DailyTaskSlot,
    daily_plan_from_dict,
    daily_plan_to_dict,
)


def _plan():
    start = datetime(2026, 10, 30, 9, tzinfo=UTC)
    slot = DailyTaskSlot("task", start, start + timedelta(minutes=30), 4.25)
    return DailyTaskPlan(date(2026, 10, 30), (slot,), ("later",), 30)


def test_daily_plan_mapping_roundtrips() -> None:
    assert daily_plan_from_dict(daily_plan_to_dict(_plan())) == _plan()


def test_daily_plan_mapping_has_golden_keys() -> None:
    encoded = daily_plan_to_dict(_plan())
    assert list(encoded) == [
        "schema_version",
        "day",
        "slots",
        "unscheduled_task_ids",
        "effort_minutes",
    ]
    assert list(encoded["slots"][0]) == ["task_id", "starts_at", "ends_at", "priority"]


def test_daily_plan_codec_rejects_extensions() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = daily_plan_to_dict(_plan())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        daily_plan_from_dict(encoded)


def test_daily_plan_codec_rejects_non_array_slots() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = daily_plan_to_dict(_plan())
    encoded["slots"] = {}
    with pytest.raises(ValidationError, match="arrays"):
        daily_plan_from_dict(encoded)
