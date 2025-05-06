"""Seeded habit check-in factory with planted lapse patterns."""

from __future__ import annotations

from datetime import date, time, timedelta

from diurnix.calendar import local_datetime
from diurnix.event_stream import event_manifest
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


def plant_habit_lapse(
    events: tuple[HabitCheckIn, ...], habit: str, start: date, *, days: int = 3
) -> tuple[HabitCheckIn, ...]:
    """Replace a consecutive date range with labeled missed observations."""
    if days < 1:
        from diurnix.errors import ValidationError

        raise ValidationError("habit lapse days must be positive")
    lapse_dates = {(start + timedelta(days=offset)).isoformat() for offset in range(days)}
    result = []
    for item in events:
        if item.habit == habit and item.local_date in lapse_dates:
            item = HabitCheckIn(
                item.event_id,
                item.occurred_at,
                item.habit,
                item.local_date,
                HabitStatus.MISSED,
                value=0.0,
                planted_lapse=True,
            )
        result.append(item)
    return tuple(result)


def mark_grace_skip(event: HabitCheckIn) -> HabitCheckIn:
    """Convert an ordinary miss into an intentional grace-day skip."""
    if event.status is not HabitStatus.MISSED or event.planted_lapse:
        from diurnix.errors import ValidationError

        raise ValidationError("only ordinary missed check-ins can become grace skips")
    return HabitCheckIn(
        event.event_id,
        event.occurred_at,
        event.habit,
        event.local_date,
        HabitStatus.SKIPPED,
        value=event.value,
        planted_lapse=False,
    )


def habit_ground_truth(events: tuple[HabitCheckIn, ...]) -> dict[str, object]:
    """Describe planted lapse identities and observed status counts."""
    return {
        "checkin_count": len(events),
        "lapse_ids": [item.event_id for item in events if item.planted_lapse],
        "status_counts": {
            status.value: sum(item.status is status for item in events) for status in HabitStatus
        },
    }


def planted_lapse_spans(events: tuple[HabitCheckIn, ...]) -> dict[str, tuple[str, str, int]]:
    """Summarize consecutive planted lapse bounds by habit."""
    result: dict[str, tuple[str, str, int]] = {}
    habits = {item.habit for item in events if item.planted_lapse}
    for habit in sorted(habits):
        dates = sorted(
            item.local_date for item in events if item.habit == habit and item.planted_lapse
        )
        result[habit] = (dates[0], dates[-1], len(dates))
    return result


def habit_manifest(events: tuple[HabitCheckIn, ...], *, seed: int) -> dict[str, object]:
    """Return exact event-byte provenance and planted habit truth."""
    return {
        "factory": "diurnix.synthetic-habits",
        "factory_version": 1,
        "seed": seed,
        "events": event_manifest(events),
        "ground_truth": habit_ground_truth(events),
    }
