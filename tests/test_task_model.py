from __future__ import annotations

from datetime import UTC, datetime

from diurnix.tasks_app import TaskStatus, make_task

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def test_task_defaults_to_gtd_inbox() -> None:
    task = make_task("task-1", "整理计划", NOW)
    assert task.status is TaskStatus.INBOX
    assert task.importance == 3 and task.effort_minutes == 30
    assert task.context == "anywhere"


def test_task_status_schema_is_stable() -> None:
    assert tuple(item.value for item in TaskStatus) == (
        "inbox",
        "next",
        "scheduled",
        "waiting",
        "someday",
        "done",
    )
