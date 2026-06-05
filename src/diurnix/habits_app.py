"""Timezone-safe habit streaks and routine scheduling."""

from __future__ import annotations

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn


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
