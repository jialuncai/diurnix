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


def capture_task(text: str, captured_at: datetime) -> TaskItem:
    from diurnix.identifiers import stable_identifier

    normalized = " ".join(text.split())
    if not normalized:
        raise ValidationError("captured task text must not be blank")
    task_id = stable_identifier(
        "task", {"text": normalized, "captured_at": captured_at.isoformat()}, length=16
    )
    return make_task(task_id, normalized, captured_at)


class Clarification(StrEnum):
    ACTIONABLE = "actionable"
    REFERENCE = "reference"
    SOMEDAY = "someday"
    DELETE = "delete"


def clarify_task(task: TaskItem) -> Clarification:
    text = task.title.casefold()
    if any(cue in text for cue in ("垃圾", "delete", "无需处理")):
        return Clarification.DELETE
    if any(cue in text for cue in ("参考", "reference", "资料")):
        return Clarification.REFERENCE
    if any(cue in text for cue in ("也许", "someday", "将来")):
        return Clarification.SOMEDAY
    return Clarification.ACTIONABLE


def organize_task(task: TaskItem, clarification: Clarification) -> TaskItem | None:
    from dataclasses import replace

    if task.status is not TaskStatus.INBOX:
        raise ValidationError("only inbox tasks can be organized")
    if clarification in (Clarification.DELETE, Clarification.REFERENCE):
        return None
    target = TaskStatus.SOMEDAY if clarification is Clarification.SOMEDAY else TaskStatus.NEXT
    if task.deadline is not None and target is TaskStatus.NEXT:
        target = TaskStatus.SCHEDULED
    return replace(task, status=target)


@dataclass(frozen=True, slots=True)
class TaskStore:
    tasks: tuple[TaskItem, ...] = ()

    def add(self, task: TaskItem) -> TaskStore:
        if any(item.task_id == task.task_id for item in self.tasks):
            raise ValidationError(f"duplicate task: {task.task_id}")
        return TaskStore((*self.tasks, task))

    def transition(self, task_id: str, status: TaskStatus) -> TaskStore:
        from dataclasses import replace

        if not any(item.task_id == task_id for item in self.tasks):
            raise ValidationError(f"unknown task: {task_id}")
        return TaskStore(
            tuple(
                replace(item, status=status) if item.task_id == task_id else item
                for item in self.tasks
            )
        )

    def by_status(self, status: TaskStatus) -> tuple[TaskItem, ...]:
        return tuple(item for item in self.tasks if item.status is status)


def task_priority(task: TaskItem, now: datetime) -> float:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValidationError("priority time must be timezone-aware")
    if task.deadline is None:
        urgency = 0.25
    else:
        days = max(0.0, (task.deadline - now).total_seconds() / 86400)
        urgency = 1.0 / (1.0 + days)
    effort_factor = 1.0 + task.effort_minutes / 60
    return round((task.importance * urgency * 10) / effort_factor, 6)


def rank_tasks(tasks: tuple[TaskItem, ...], now: datetime) -> tuple[TaskItem, ...]:
    actionable = tuple(
        task for task in tasks if task.status in (TaskStatus.NEXT, TaskStatus.SCHEDULED)
    )
    return tuple(
        sorted(
            actionable,
            key=lambda task: (
                -task_priority(task, now),
                task.deadline or datetime.max.replace(tzinfo=now.tzinfo),
                task.task_id,
            ),
        )
    )
