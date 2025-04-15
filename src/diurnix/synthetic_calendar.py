"""Seeded calendar factory with planted conflicts and travel constraints."""

from __future__ import annotations

from datetime import date, time, timedelta

from diurnix.calendar import local_datetime
from diurnix.events import CalendarEntry
from diurnix.persona import Persona
from diurnix.randomness import SeededRandom

_TITLES = ("合成讨论", "离线复盘", "日程整理", "课程准备")
_LOCATIONS = ("home", "campus", "library")


def generate_calendar_entry(
    persona: Persona, seed: int, index: int, day: date, *, hour: int = 10
) -> CalendarEntry:
    """Generate one local appointment with deterministic duration and location."""
    random = SeededRandom(seed).fork(f"calendar-{index}")
    starts_at = local_datetime(day, time(hour), persona.timezone)
    duration = random.choice((30, 45, 60, 90))
    return CalendarEntry(
        f"calendar_{seed}_{index}",
        starts_at,
        random.choice(_TITLES),
        starts_at,
        starts_at + timedelta(minutes=duration),
        random.choice(_LOCATIONS),
    )


def generate_calendar_week(persona: Persona, seed: int, start: date) -> tuple[CalendarEntry, ...]:
    """Generate morning and afternoon appointments on configured workdays."""
    result = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        if day.weekday() not in persona.work_hours.weekdays:
            continue
        result.append(generate_calendar_entry(persona, seed, len(result), day, hour=10))
        result.append(generate_calendar_entry(persona, seed, len(result), day, hour=14))
    return tuple(result)


def plant_calendar_conflict(source: CalendarEntry, seed: int, index: int) -> CalendarEntry:
    """Create a labeled interval that overlaps the middle of ``source``."""
    start = source.starts_at + timedelta(minutes=max(1, source.duration_minutes // 2))
    return CalendarEntry(
        f"calendar_conflict_{seed}_{index}",
        start,
        "合成冲突",
        start,
        source.ends_at + timedelta(minutes=15),
        source.location,
        planted_conflict=True,
    )


def calendar_week_with_conflict(
    persona: Persona, seed: int, start: date
) -> tuple[CalendarEntry, ...]:
    """Generate one week and plant one explicit overlapping pair."""
    base = list(generate_calendar_week(persona, seed, start))
    if base:
        base.append(plant_calendar_conflict(base[2], seed, 0))
    return tuple(sorted(base, key=lambda entry: (entry.starts_at, entry.event_id)))
