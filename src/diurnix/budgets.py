"""Immutable multi-dimensional budget accounting."""

from __future__ import annotations

from dataclasses import dataclass

from diurnix.errors import ValidationError


@dataclass(frozen=True, slots=True)
class Usage:
    """Consumed step, wall-clock, and synthetic money quantities."""

    steps: int = 0
    wall_seconds: float = 0.0
    money: float = 0.0

    def __post_init__(self) -> None:
        if self.steps < 0 or self.wall_seconds < 0 or self.money < 0:
            raise ValidationError("usage values cannot be negative")

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            self.steps + other.steps,
            round(self.wall_seconds + other.wall_seconds, 6),
            round(self.money + other.money, 6),
        )


@dataclass(frozen=True, slots=True)
class Budget:
    """Maximum allowed quantities in every runtime dimension."""

    max_steps: int
    max_wall_seconds: float
    max_money: float

    def __post_init__(self) -> None:
        if self.max_steps < 0 or self.max_wall_seconds < 0 or self.max_money < 0:
            raise ValidationError("budget limits cannot be negative")

    def allows(self, usage: Usage) -> bool:
        """Return whether usage stays within every inclusive limit."""
        return (
            usage.steps <= self.max_steps
            and usage.wall_seconds <= self.max_wall_seconds
            and usage.money <= self.max_money
        )

    def require(self, usage: Usage) -> None:
        """Raise with exceeded dimensions if usage is over budget."""
        exceeded = []
        if usage.steps > self.max_steps:
            exceeded.append("steps")
        if usage.wall_seconds > self.max_wall_seconds:
            exceeded.append("wall_seconds")
        if usage.money > self.max_money:
            exceeded.append("money")
        if exceeded:
            raise ValidationError("budget exceeded: " + ", ".join(exceeded), path="$.usage")


def remaining(budget: Budget, usage: Usage) -> Usage:
    """Return nonnegative capacity after requiring current usage to fit."""
    budget.require(usage)
    return Usage(
        budget.max_steps - usage.steps,
        round(budget.max_wall_seconds - usage.wall_seconds, 6),
        round(budget.max_money - usage.money, 6),
    )


def reserve(budget: Budget, usage: Usage, requested: Usage) -> Usage:
    """Atomically validate and return usage with a requested reservation."""
    updated = usage + requested
    budget.require(updated)
    return updated
