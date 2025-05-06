"""Seeded habit check-in factory with planted lapse patterns."""

from __future__ import annotations

from datetime import date, time

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
