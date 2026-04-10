from __future__ import annotations

from datetime import UTC, datetime

from diurnix.tasks_app import TaskStatus, TaskStore, make_task

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def _task(task_id: str, status: TaskStatus = TaskStatus.NEXT):
    return make_task(task_id, task_id, NOW, status=status)


def test_task_store_add_and_transition_return_new_values() -> None:
    original = TaskStore().add(_task("a"))
    updated = original.transition("a", TaskStatus.DONE)
    assert original.by_status(TaskStatus.NEXT) == (_task("a"),)
    assert updated.by_status(TaskStatus.DONE)[0].task_id == "a"


def test_task_store_filters_status_in_insertion_order() -> None:
    store = TaskStore((_task("a"), _task("b", TaskStatus.SOMEDAY), _task("c")))
    assert tuple(task.task_id for task in store.by_status(TaskStatus.NEXT)) == ("a", "c")
