"""Seeded synthetic persona configuration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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


@dataclass(frozen=True, slots=True)
class HabitGoal:
    """Synthetic weekly habit target used to plant check-in streams."""

    name: str
    target_days_per_week: int
    preferred_hour: int
    grace_days: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("habit goal name must not be blank")
        if not 1 <= self.target_days_per_week <= 7:
            raise ValidationError("habit target days must be from one to seven")
        if not 0 <= self.preferred_hour <= 23:
            raise ValidationError("habit preferred hour must be from zero to 23")
        if not 0 <= self.grace_days <= 3:
            raise ValidationError("habit grace days must be from zero to three")


@dataclass(frozen=True, slots=True)
class Persona:
    """Complete synthetic identity and daily-life generation configuration."""

    persona_id: str
    name: str
    timezone: str
    work_hours: WorkHours
    correspondents: tuple[Correspondent, ...]
    merchants: tuple[MerchantProfile, ...]
    habit_goals: tuple[HabitGoal, ...]

    def __post_init__(self) -> None:
        from diurnix.identifiers import validate_identifier

        validate_identifier(self.persona_id, label="persona_id")
        if not self.name.strip():
            raise ValidationError("persona name must not be blank")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as error:
            raise ValidationError("persona timezone must be an IANA name") from error
        validate_correspondents(self.correspondents)
        if not self.merchants or not self.habit_goals:
            raise ValidationError("persona requires merchants and habit goals")
        merchant_names = [item.name.casefold() for item in self.merchants]
        habit_names = [item.name.casefold() for item in self.habit_goals]
        if len(set(merchant_names)) != len(merchant_names):
            raise ValidationError("persona merchant names must be unique")
        if len(set(habit_names)) != len(habit_names):
            raise ValidationError("persona habit names must be unique")
