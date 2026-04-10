from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.tasks_app import make_task, task_priority

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def test_priority_rewards_importance_and_near_deadlines() -> None:
    low = make_task("low", "low", NOW, importance=1, effort_minutes=30)
    urgent = make_task(
        "urgent", "urgent", NOW, deadline=NOW + timedelta(hours=1), importance=5, effort_minutes=30
    )
    assert task_priority(urgent, NOW) > task_priority(low, NOW)


def test_priority_penalizes_larger_effort_for_same_value() -> None:
    short = make_task("short", "short", NOW, importance=4, effort_minutes=15)
    long = make_task("long", "long", NOW, importance=4, effort_minutes=120)
    assert task_priority(short, NOW) > task_priority(long, NOW)


def test_overdue_priority_caps_at_current_urgency() -> None:
    overdue = make_task(
        "overdue", "overdue", NOW, deadline=NOW - timedelta(days=5), importance=3, effort_minutes=60
    )
    due_now = make_task("now", "now", NOW, deadline=NOW, importance=3, effort_minutes=60)
    assert task_priority(overdue, NOW) == task_priority(due_now, NOW) == 15.0


def test_priority_rejects_naive_evaluation_time() -> None:
    import pytest

    from diurnix.errors import ValidationError

    with pytest.raises(ValidationError, match="timezone-aware"):
        task_priority(make_task("t", "t", NOW), datetime(2026, 1, 1))
