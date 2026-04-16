from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from diurnix.events import CalendarEntry
from diurnix.persona_factory import create_persona, work_bounds
from diurnix.tasks_app import TaskStatus, build_daily_task_plan, make_task

DAY = date(2026, 10, 26)
NOW = datetime(2026, 10, 26, 8, tzinfo=UTC)


def _task(task_id: str, effort: int, importance: int = 3):
    return make_task(
        task_id, task_id, NOW, importance=importance, effort_minutes=effort, status=TaskStatus.NEXT
    )


def test_daily_plan_avoids_calendar_and_travel_buffers() -> None:
    persona = create_persona(1)
    work_start, _ = work_bounds(persona, DAY)
    meeting = CalendarEntry(
        "meeting",
        work_start,
        "meeting",
        work_start + timedelta(minutes=30),
        work_start + timedelta(minutes=60),
        "campus",
        15,
    )
    plan = build_daily_task_plan((_task("task", 30),), (meeting,), persona, DAY, NOW)
    assert len(plan.slots) == 1
    assert plan.slots[0].ends_at <= meeting.starts_at - timedelta(minutes=15) or plan.slots[
        0
    ].starts_at >= meeting.ends_at + timedelta(minutes=15)


def test_daily_plan_returns_actionable_tasks_only() -> None:
    persona = create_persona(1)
    someday = make_task("later", "later", NOW, status=TaskStatus.SOMEDAY)
    plan = build_daily_task_plan((_task("next", 30), someday), (), persona, DAY, NOW)
    assert tuple(slot.task_id for slot in plan.slots) == ("next",)
