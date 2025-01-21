"""Timezone-aware calendar arithmetic for synthetic schedules."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from diurnix.errors import ValidationError


def timezone(name: str) -> ZoneInfo:
    """Resolve an IANA timezone with a structured validation error."""
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as error:
        raise ValidationError("unknown IANA timezone", path="$.timezone") from error


def local_datetime(day: date, wall_time: time, zone: str, *, fold: int = 0) -> datetime:
    """Construct a local datetime and reject nonexistent wall-clock instants."""
    if fold not in (0, 1):
        raise ValidationError("fold must be zero or one", path="$.fold")
    tz = timezone(zone)
    candidate = datetime.combine(day, wall_time, tzinfo=tz).replace(fold=fold)
    roundtrip = candidate.astimezone(ZoneInfo("UTC")).astimezone(tz)
    if roundtrip.replace(fold=fold) != candidate:
        raise ValidationError("wall-clock time does not exist", path="$.time")
    return candidate


def add_calendar_days(moment: datetime, days: int) -> datetime:
    """Shift a local calendar date while preserving wall time across DST."""
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValidationError("moment must be timezone-aware", path="$.moment")
    return datetime.combine(moment.date() + timedelta(days=days), moment.timetz())


def date_span(start: date, end: date) -> tuple[date, ...]:
    """Return an inclusive ordered date span."""
    if end < start:
        raise ValidationError("date span end precedes start", path="$.end")
    return tuple(start + timedelta(days=offset) for offset in range((end - start).days + 1))


def week_start(day: date, *, first_weekday: int = 0) -> date:
    """Return the configured first weekday at or before a date."""
    if not 0 <= first_weekday <= 6:
        raise ValidationError("first weekday must be from zero to six", path="$.first_weekday")
    return day - timedelta(days=(day.weekday() - first_weekday) % 7)
