"""Seeded synthetic persona configuration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from diurnix.errors import ValidationError


@dataclass(frozen=True, slots=True)
class WorkHours:
    """Local work window and active weekdays using Monday as zero."""

    starts_at: time
    ends_at: time
    weekdays: tuple[int, ...] = (0, 1, 2, 3, 4)

    def __post_init__(self) -> None:
        if self.starts_at >= self.ends_at:
            raise ValidationError("work hours must have positive same-day duration")
        if not self.weekdays or len(set(self.weekdays)) != len(self.weekdays):
            raise ValidationError("work weekdays must be nonempty and unique")
        if any(day < 0 or day > 6 for day in self.weekdays):
            raise ValidationError("work weekdays must be from zero to six")

    def contains(self, weekday: int, wall_time: time) -> bool:
        """Return whether a local wall time is in the half-open work window."""
        return weekday in self.weekdays and self.starts_at <= wall_time < self.ends_at
