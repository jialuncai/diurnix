"""Timezone-safe habit streaks and routine scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus


def group_habit_checkins(events: tuple[HabitCheckIn, ...]) -> dict[str, tuple[HabitCheckIn, ...]]:
    grouped: dict[str, list[HabitCheckIn]] = {}
    for event in events:
        grouped.setdefault(event.habit, []).append(event)
    result = {}
    for habit, items in sorted(grouped.items()):
        ordered = tuple(sorted(items, key=lambda item: (item.local_date, item.event_id)))
        if len({item.local_date for item in ordered}) != len(ordered):
            raise ValidationError(f"duplicate local habit date: {habit}")
        result[habit] = ordered
    return result


@dataclass(frozen=True, slots=True)
class StreakSummary:
    habit: str
    current: int
    longest: int
    done_days: int
    grace_days_used: int


def calculate_streak(events: tuple[HabitCheckIn, ...], *, grace_days: int = 0) -> StreakSummary:
    if grace_days < 0:
        raise ValidationError("streak grace days cannot be negative")
    if not events:
        return StreakSummary("", 0, 0, 0, 0)
    grouped = group_habit_checkins(events)
    if len(grouped) != 1:
        raise ValidationError("streak calculation requires one habit")
    habit, ordered = next(iter(grouped.items()))
    current = longest = done_days = grace_used = grace_in_streak = 0
    previous_day = None
    for event in ordered:
        day = date.fromisoformat(event.local_date)
        if previous_day is not None and (day - previous_day).days != 1:
            current = 0
            grace_in_streak = 0
        if event.status is HabitStatus.DONE:
            current += 1
            done_days += 1
        elif event.status is HabitStatus.SKIPPED and grace_in_streak < grace_days:
            current += 1
            grace_in_streak += 1
            grace_used += 1
        else:
            current = 0
            grace_in_streak = 0
        longest = max(longest, current)
        previous_day = day
    return StreakSummary(habit, current, longest, done_days, grace_used)


def streak_for_goal(events: tuple[HabitCheckIn, ...], goal: object) -> StreakSummary:
    from diurnix.persona import HabitGoal

    if not isinstance(goal, HabitGoal):
        raise ValidationError("streak goal has wrong type")
    selected = tuple(event for event in events if event.habit == goal.name)
    return calculate_streak(selected, grace_days=goal.grace_days)


def habit_consistency(events: tuple[HabitCheckIn, ...], target_days_per_week: int) -> float:
    if not 1 <= target_days_per_week <= 7:
        raise ValidationError("habit target must be from one to seven")
    if not events:
        return 0.0
    ordered = next(iter(group_habit_checkins(events).values()))
    span_days = (
        date.fromisoformat(ordered[-1].local_date) - date.fromisoformat(ordered[0].local_date)
    ).days + 1
    expected = target_days_per_week * span_days / 7
    done = sum(event.status is HabitStatus.DONE for event in ordered)
    return round(min(1.0, done / expected), 6) if expected else 0.0
