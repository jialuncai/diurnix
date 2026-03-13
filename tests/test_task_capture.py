from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.tasks_app import TaskStatus, capture_task

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def test_task_capture_normalizes_whitespace_and_stabilizes_id() -> None:
    first = capture_task("  完成   周报 ", NOW)
    second = capture_task("完成 周报", NOW)
    assert first == second
    assert first.title == "完成 周报" and first.status is TaskStatus.INBOX


def test_task_capture_rejects_blank_text() -> None:
    with pytest.raises(ValidationError, match="blank"):
        capture_task(" \n ", NOW)
