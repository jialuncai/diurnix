from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.tasks_app import Clarification, TaskStatus, capture_task, make_task, organize_task

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def test_organize_routes_actionable_and_someday_items() -> None:
    task = capture_task("完成周报", NOW)
    assert organize_task(task, Clarification.ACTIONABLE).status is TaskStatus.NEXT
    assert organize_task(task, Clarification.SOMEDAY).status is TaskStatus.SOMEDAY


def test_organize_routes_deadlined_action_to_scheduled() -> None:
    task = make_task("t", "准备会议", NOW, deadline=NOW + timedelta(days=1))
    assert organize_task(task, Clarification.ACTIONABLE).status is TaskStatus.SCHEDULED


def test_organize_drops_reference_and_delete_items() -> None:
    task = capture_task("参考资料", NOW)
    assert organize_task(task, Clarification.REFERENCE) is None
    assert organize_task(task, Clarification.DELETE) is None
