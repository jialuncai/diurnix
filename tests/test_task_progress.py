from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.tasks_app import (
    TaskStatus,
    apply_task_progress,
    make_task,
    record_task_progress,
)

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)
TASK = make_task("task", "task", NOW, effort_minutes=30, status=TaskStatus.NEXT)


def test_task_progress_caps_minutes_and_marks_done() -> None:
    progress = record_task_progress(TASK, 40, NOW)
    assert progress.completed_minutes == 30 and progress.done is True
    assert apply_task_progress(TASK, progress).status is TaskStatus.DONE


def test_partial_progress_preserves_task_status() -> None:
    progress = record_task_progress(TASK, 10, NOW)
    assert apply_task_progress(TASK, progress) == TASK


def test_task_progress_rejects_negative_minutes() -> None:
    with pytest.raises(ValidationError, match="negative"):
        record_task_progress(TASK, -1, NOW)
