"""GTD-style capture, organization, and deterministic daily planning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum

from diurnix.errors import ValidationError
from diurnix.events import CalendarEntry
from diurnix.persona import Persona
from diurnix.persona_factory import work_bounds


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


@dataclass(frozen=True, slots=True)
class DailyTaskSlot:
    task_id: str
    starts_at: datetime
    ends_at: datetime
    priority: float


@dataclass(frozen=True, slots=True)
class DailyTaskPlan:
    day: date
    slots: tuple[DailyTaskSlot, ...]
    unscheduled_task_ids: tuple[str, ...]
    effort_minutes: int


def build_daily_task_plan(
    tasks: tuple[TaskItem, ...],
    calendar: tuple[CalendarEntry, ...],
    persona: Persona,
    day: date,
    now: datetime,
    *,
    max_tasks: int = 8,
    max_effort_minutes: int = 240,
) -> DailyTaskPlan:
    if max_tasks < 0 or max_effort_minutes < 0:
        raise ValidationError("daily task budgets cannot be negative")
    ranked = rank_tasks(tasks, now)
    bounds = work_bounds(persona, day)
    if bounds is None:
        return DailyTaskPlan(day, (), tuple(task.task_id for task in ranked), 0)
    work_start, work_end = bounds
    busy = sorted(
        (
            entry.starts_at - timedelta(minutes=entry.travel_minutes),
            entry.ends_at + timedelta(minutes=entry.travel_minutes),
        )
        for entry in calendar
        if entry.starts_at.astimezone(work_start.tzinfo).date() == day
    )
    slots = []
    unscheduled = []
    used_effort = 0
    for task in ranked:
        if len(slots) >= max_tasks or used_effort + task.effort_minutes > max_effort_minutes:
            unscheduled.append(task.task_id)
            continue
        duration = timedelta(minutes=task.effort_minutes)
        candidate = work_start
        for blocked_start, blocked_end in sorted(busy):
            if candidate + duration <= blocked_start:
                break
            if candidate < blocked_end:
                candidate = blocked_end
        if candidate + duration > work_end:
            unscheduled.append(task.task_id)
            continue
        slot = DailyTaskSlot(
            task.task_id, candidate, candidate + duration, task_priority(task, now)
        )
        slots.append(slot)
        busy.append((slot.starts_at, slot.ends_at))
        used_effort += task.effort_minutes
    return DailyTaskPlan(day, tuple(slots), tuple(unscheduled), used_effort)


def daily_plan_to_dict(plan: DailyTaskPlan) -> dict[str, object]:
    return {
        "schema_version": 1,
        "day": plan.day.isoformat(),
        "slots": [
            {
                "task_id": slot.task_id,
                "starts_at": slot.starts_at.isoformat(),
                "ends_at": slot.ends_at.isoformat(),
                "priority": slot.priority,
            }
            for slot in plan.slots
        ],
        "unscheduled_task_ids": list(plan.unscheduled_task_ids),
        "effort_minutes": plan.effort_minutes,
    }


def daily_plan_from_dict(value: dict[str, object]) -> DailyTaskPlan:
    expected = {"schema_version", "day", "slots", "unscheduled_task_ids", "effort_minutes"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("daily task plan does not match schema")
    slots_value = value["slots"]
    unscheduled = value["unscheduled_task_ids"]
    if not isinstance(slots_value, list) or not isinstance(unscheduled, list):
        raise ValidationError("daily task plan arrays are invalid")
    try:
        slots = tuple(
            DailyTaskSlot(
                str(item["task_id"]),
                datetime.fromisoformat(str(item["starts_at"])),
                datetime.fromisoformat(str(item["ends_at"])),
                float(item["priority"]),
            )
            for item in slots_value
        )
        return DailyTaskPlan(
            date.fromisoformat(str(value["day"])),
            slots,
            tuple(str(item) for item in unscheduled),
            int(value["effort_minutes"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid daily task plan value") from error


@dataclass(frozen=True, slots=True)
class TaskProgress:
    task_id: str
    completed_minutes: int
    observed_at: datetime
    done: bool


def record_task_progress(
    task: TaskItem, completed_minutes: int, observed_at: datetime
) -> TaskProgress:
    if completed_minutes < 0:
        raise ValidationError("completed task minutes cannot be negative")
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValidationError("task progress time must be timezone-aware")
    bounded = min(completed_minutes, task.effort_minutes)
    return TaskProgress(task.task_id, bounded, observed_at, bounded == task.effort_minutes)


def apply_task_progress(task: TaskItem, progress: TaskProgress) -> TaskItem:
    from dataclasses import replace

    if task.task_id != progress.task_id:
        raise ValidationError("task progress identity mismatch")
    return replace(task, status=TaskStatus.DONE) if progress.done else task


@dataclass(frozen=True, slots=True)
class TaskSlippage:
    task_id: str
    planned_minutes: int
    completed_minutes: int
    overdue: bool


def detect_task_slippage(
    plan: DailyTaskPlan,
    tasks: tuple[TaskItem, ...],
    progress: tuple[TaskProgress, ...],
    as_of: datetime,
) -> tuple[TaskSlippage, ...]:
    task_by_id = {task.task_id: task for task in tasks}
    completed = {item.task_id: item.completed_minutes for item in progress}
    result = []
    for slot in plan.slots:
        task = task_by_id[slot.task_id]
        actual = completed.get(slot.task_id, 0)
        due = slot.ends_at <= as_of
        if due and actual < task.effort_minutes:
            overdue = task.deadline is not None and task.deadline < as_of
            result.append(TaskSlippage(task.task_id, task.effort_minutes, actual, overdue))
    return tuple(result)
