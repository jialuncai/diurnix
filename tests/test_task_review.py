from __future__ import annotations

from datetime import UTC, datetime

from diurnix.tasks_app import TaskSlippage, TaskStatus, make_task, weekly_task_review

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def _task(task_id: str, status: TaskStatus):
    return make_task(task_id, task_id, NOW, status=status)


def test_weekly_review_measures_executed_task_states() -> None:
    tasks = (_task("done", TaskStatus.DONE), _task("next", TaskStatus.NEXT))
    slipped = (TaskSlippage("next", 30, 0, False),)
    review = weekly_task_review(tasks, slipped)
    assert review["completed_count"] == 1 and review["actionable_count"] == 1
    assert review["completion_rate"] == 0.5
    assert review["slipped_task_ids"] == ["next"]


def test_weekly_review_labels_synthetic_results() -> None:
    assert weekly_task_review((), ())["synthetic"] is True


def test_empty_weekly_review_is_explicit() -> None:
    assert weekly_task_review((), ()) == {
        "task_count": 0,
        "completed_count": 0,
        "actionable_count": 0,
        "someday_count": 0,
        "slipped_task_ids": [],
        "completion_rate": 0.0,
        "synthetic": True,
    }


def test_someday_tasks_do_not_distort_completion_rate() -> None:
    tasks = (_task("done", TaskStatus.DONE), _task("later", TaskStatus.SOMEDAY))
    assert weekly_task_review(tasks, ())["completion_rate"] == 1.0
