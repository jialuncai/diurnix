from __future__ import annotations

import itertools
from datetime import UTC, date, datetime

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict
from diurnix.tasks_app import TaskStatus, build_daily_task_plan, make_task


def _run(seed: int):
    day = date(2026, 10, 26)
    now = datetime(2026, 10, 26, 8, tzinfo=UTC)
    persona = create_persona(seed)
    calendar = calendar_week_with_conflict(persona, seed, day)
    tasks = tuple(
        make_task(
            f"task-{index}",
            f"合成任务 {index}",
            now,
            importance=index + 1,
            effort_minutes=30,
            status=TaskStatus.NEXT,
        )
        for index in range(4)
    )
    return build_daily_task_plan(tasks, calendar, persona, day, now)


def test_same_seed_produces_identical_daily_plan() -> None:
    assert _run(7) == _run(7)


def test_seeded_plan_has_nonoverlapping_task_slots() -> None:
    plan = _run(7)
    for left, right in itertools.pairwise(plan.slots):
        assert left.ends_at <= right.starts_at
