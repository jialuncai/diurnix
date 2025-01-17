"""Deterministic time source for offline runs."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from diurnix.errors import ValidationError


@dataclass(order=True, frozen=True, slots=True)
class ScheduledTimer:
    """A stable timer ordered by instant and insertion sequence."""

    when: datetime
    sequence: int
    name: str = field(compare=False)


class SyntheticClock:
    """A manually advanced clock with deterministic timer ordering."""

    def __init__(self, start: datetime) -> None:
        if start.tzinfo is None or start.utcoffset() is None:
            raise ValidationError("clock start must be timezone-aware", path="$.start")
        self._now = start
        self._sequence = 0
        self._timers: list[ScheduledTimer] = []

    def now(self) -> datetime:
        """Return the current synthetic instant."""
        return self._now

    def schedule(self, name: str, when: datetime) -> ScheduledTimer:
        """Schedule a named timer at or after the current instant."""
        if not name:
            raise ValidationError("timer name must not be empty", path="$.name")
        if when.tzinfo is None or when.utcoffset() is None:
            raise ValidationError("timer instant must be timezone-aware", path="$.when")
        if when < self._now:
            raise ValidationError("timer cannot be scheduled in the past", path="$.when")
        timer = ScheduledTimer(when, self._sequence, name)
        self._sequence += 1
        heapq.heappush(self._timers, timer)
        return timer

    def advance(self, duration: timedelta) -> tuple[ScheduledTimer, ...]:
        """Move forward and return all timers due by the new instant."""
        if duration < timedelta(0):
            raise ValidationError("clock cannot move backward", path="$.duration")
        self._now += duration
        due: list[ScheduledTimer] = []
        while self._timers and self._timers[0].when <= self._now:
            due.append(heapq.heappop(self._timers))
        return tuple(due)

    def pending(self) -> tuple[ScheduledTimer, ...]:
        """Return pending timers in firing order without consuming them."""
        return tuple(sorted(self._timers))
