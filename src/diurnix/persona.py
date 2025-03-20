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


@dataclass(frozen=True, slots=True)
class Correspondent:
    """Synthetic contact used only by the offline factory."""

    name: str
    email: str
    relationship: str
    trusted: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.relationship.strip():
            raise ValidationError("correspondent name and relationship must not be blank")
        if "@" not in self.email or self.email.startswith("@") or self.email.endswith("@"):
            raise ValidationError("correspondent email is invalid", path="$.email")


def validate_correspondents(items: tuple[Correspondent, ...]) -> None:
    """Require usable and unique synthetic contact identities."""
    if not items:
        raise ValidationError("persona requires at least one correspondent")
    emails = [item.email.casefold() for item in items]
    if len(set(emails)) != len(emails):
        raise ValidationError("correspondent emails must be unique")


@dataclass(frozen=True, slots=True)
class MerchantProfile:
    """Synthetic merchant baseline for planted transaction anomalies."""

    name: str
    category: str
    typical_amount: float
    recurring: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.category.strip():
            raise ValidationError("merchant name and category must not be blank")
        if self.typical_amount <= 0 or self.typical_amount == float("inf"):
            raise ValidationError("typical merchant amount must be positive and finite")


def merchant_categories(items: tuple[MerchantProfile, ...]) -> tuple[str, ...]:
    """Return first-seen category order without duplicates."""
    return tuple(dict.fromkeys(item.category for item in items))
