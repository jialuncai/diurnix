"""Seeded habit check-in factory with planted lapse patterns."""

from __future__ import annotations

from datetime import date, time, timedelta

from diurnix.calendar import local_datetime
from diurnix.events import HabitCheckIn, HabitStatus
from diurnix.persona import HabitGoal, Persona
from diurnix.randomness import SeededRandom


def generate_habit_checkin(
    persona: Persona, goal: HabitGoal, seed: int, index: int, day: date
) -> HabitCheckIn:
    """Generate one reproducible local-day observation for a habit goal."""
    random = SeededRandom(seed).fork(f"habit-{goal.name}-{index}")
    completed = random.integer(0, 100) < round(goal.target_days_per_week / 7 * 100)
    status = HabitStatus.DONE if completed else HabitStatus.MISSED
    occurred = local_datetime(day, time(goal.preferred_hour), persona.timezone)
    return HabitCheckIn(
        f"habit_{seed}_{index}",
        occurred,
        goal.name,
        day.isoformat(),
        status,
        value=1.0 if completed else 0.0,
    )


def generate_habit_stream(
    persona: Persona, seed: int, start: date, *, days: int = 30
) -> tuple[HabitCheckIn, ...]:
    """Generate one check-in per persona goal per local day."""
    from diurnix.errors import ValidationError

    if not 1 <= days <= 366:
        raise ValidationError("habit stream days must be from one to 366")
    result = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        for goal_index, goal in enumerate(persona.habit_goals):
            index = offset * len(persona.habit_goals) + goal_index
            result.append(generate_habit_checkin(persona, goal, seed, index, day))
    return tuple(result)
