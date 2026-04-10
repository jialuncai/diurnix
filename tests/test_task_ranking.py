from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.tasks_app import TaskStatus, make_task, rank_tasks

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def _task(task_id: str, importance: int, status: TaskStatus = TaskStatus.NEXT):
    return make_task(
        task_id,
        task_id,
        NOW,
        deadline=NOW + timedelta(days=1),
        importance=importance,
        effort_minutes=30,
        status=status,
    )


def test_task_ranking_orders_score_then_identity() -> None:
    ranked = rank_tasks((_task("b", 3), _task("high", 5), _task("a", 3)), NOW)
    assert tuple(task.task_id for task in ranked) == ("high", "a", "b")


def test_task_ranking_excludes_nonactionable_statuses() -> None:
    ranked = rank_tasks((_task("next", 3), _task("someday", 5, TaskStatus.SOMEDAY)), NOW)
    assert tuple(task.task_id for task in ranked) == ("next",)
