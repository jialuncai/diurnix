"""GTD-style capture, organization, and deterministic daily planning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from diurnix.errors import ValidationError


class TaskStatus(StrEnum):
    INBOX = "inbox"
    NEXT = "next"
    SCHEDULED = "scheduled"
    WAITING = "waiting"
    SOMEDAY = "someday"
    DONE = "done"


@dataclass(frozen=True, slots=True)
class TaskItem:
    task_id: str
    title: str
    captured_at: datetime
    deadline: datetime | None
    importance: int
    effort_minutes: int
    status: TaskStatus = TaskStatus.INBOX
    context: str = "anywhere"


def make_task(
    task_id: str,
    title: str,
    captured_at: datetime,
    *,
    deadline: datetime | None = None,
    importance: int = 3,
    effort_minutes: int = 30,
    status: TaskStatus = TaskStatus.INBOX,
    context: str = "anywhere",
) -> TaskItem:
    if not task_id.strip() or not title.strip():
        raise ValidationError("task id and title must not be blank")
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise ValidationError("task capture time must be timezone-aware")
    if deadline is not None and (deadline.tzinfo is None or deadline.utcoffset() is None):
        raise ValidationError("task deadline must be timezone-aware")
    if not 1 <= importance <= 5:
        raise ValidationError("task importance must be from one to five")
    if effort_minutes < 1:
        raise ValidationError("task effort must be positive")
    if not context.strip():
        raise ValidationError("task context must not be blank")
    return TaskItem(
        task_id, title, captured_at, deadline, importance, effort_minutes, status, context
    )


def task_to_dict(task: TaskItem) -> dict[str, object]:
    return {
        "schema_version": 1,
        "task_id": task.task_id,
        "title": task.title,
        "captured_at": task.captured_at.isoformat(),
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "importance": task.importance,
        "effort_minutes": task.effort_minutes,
        "status": task.status.value,
        "context": task.context,
    }


def task_from_dict(value: dict[str, object]) -> TaskItem:
    expected = {
        "schema_version",
        "task_id",
        "title",
        "captured_at",
        "deadline",
        "importance",
        "effort_minutes",
        "status",
        "context",
    }
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("task does not match schema")
    try:
        deadline = (
            None if value["deadline"] is None else datetime.fromisoformat(str(value["deadline"]))
        )
        return make_task(
            str(value["task_id"]),
            str(value["title"]),
            datetime.fromisoformat(str(value["captured_at"])),
            deadline=deadline,
            importance=int(value["importance"]),
            effort_minutes=int(value["effort_minutes"]),
            status=TaskStatus(str(value["status"])),
            context=str(value["context"]),
        )
    except (TypeError, ValueError) as error:
        raise ValidationError(f"invalid task value: {error}") from error
