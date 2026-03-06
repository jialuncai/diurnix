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


def test_task_rejects_blank_identity_and_nonpositive_effort() -> None:
    import pytest

    from diurnix.errors import ValidationError

    with pytest.raises(ValidationError, match="blank"):
        make_task("", "title", NOW)
    with pytest.raises(ValidationError, match="positive"):
        make_task("task", "title", NOW, effort_minutes=0)


def test_task_validates_importance_and_aware_times() -> None:
    import pytest

    from diurnix.errors import ValidationError

    with pytest.raises(ValidationError, match="importance"):
        make_task("task", "title", NOW, importance=6)
    with pytest.raises(ValidationError, match="capture"):
        make_task("task", "title", datetime(2026, 1, 1))
    with pytest.raises(ValidationError, match="deadline"):
        make_task("task", "title", NOW, deadline=datetime(2026, 1, 2))
