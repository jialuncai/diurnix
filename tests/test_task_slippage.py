from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from diurnix.tasks_app import (
    DailyTaskPlan,
    DailyTaskSlot,
    TaskStatus,
    detect_task_slippage,
    make_task,
    record_task_progress,
)

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)
TASK = make_task(
    "task",
    "task",
    NOW,
    deadline=NOW + timedelta(minutes=20),
    effort_minutes=30,
    status=TaskStatus.SCHEDULED,
)
PLAN = DailyTaskPlan(
    date(2026, 10, 30), (DailyTaskSlot("task", NOW, NOW + timedelta(minutes=30), 5.0),), (), 30
)


def test_slippage_reports_elapsed_incomplete_slot() -> None:
    progress = (record_task_progress(TASK, 10, NOW + timedelta(minutes=15)),)
    slippage = detect_task_slippage(PLAN, (TASK,), progress, NOW + timedelta(hours=1))
    assert slippage[0].completed_minutes == 10
    assert slippage[0].planned_minutes == 30 and slippage[0].overdue is True


def test_slippage_ignores_slot_before_end() -> None:
    assert detect_task_slippage(PLAN, (TASK,), (), NOW + timedelta(minutes=10)) == ()


def test_completed_task_is_not_slipping() -> None:
    progress = (record_task_progress(TASK, 30, NOW + timedelta(minutes=25)),)
    assert detect_task_slippage(PLAN, (TASK,), progress, NOW + timedelta(hours=1)) == ()


def test_missing_progress_counts_as_zero_after_slot() -> None:
    slippage = detect_task_slippage(PLAN, (TASK,), (), NOW + timedelta(hours=1))
    assert slippage == (
        type(slippage[0])("task", planned_minutes=30, completed_minutes=0, overdue=True),
    )
