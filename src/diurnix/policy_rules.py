"""Reusable declarative and conditional policy rule helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from zoneinfo import ZoneInfo

from diurnix.errors import ValidationError
from diurnix.policy import PolicyAction, PolicyEffect, PolicyRule


@dataclass(frozen=True, slots=True)
class MoneyThresholdRule(PolicyRule):
    """Match monetary actions at or above an absolute threshold."""

    threshold: float = 0.0
    amount_field: str = "amount"

    def __post_init__(self) -> None:
        PolicyRule.__post_init__(self)
        if self.threshold < 0:
            raise ValidationError("money threshold cannot be negative")

    def matches(self, action: PolicyAction) -> bool:
        if not PolicyRule.matches(self, action):
            return False
        amount = action.arguments.get(self.amount_field)
        return (
            isinstance(amount, (int, float))
            and not isinstance(amount, bool)
            and abs(amount) >= self.threshold
        )


def money_approval(threshold: float) -> MoneyThresholdRule:
    """Build the standard synthetic-money approval rule."""
    return MoneyThresholdRule(
        "money_approval",
        PolicyEffect.ASK,
        f"amount reaches {threshold:g}",
        priority=50,
        capabilities=("money.write",),
        threshold=threshold,
    )


@dataclass(frozen=True, slots=True)
class OutsideTimeWindowRule(PolicyRule):
    """Match actions outside a local half-open allowed window."""

    starts_at: time = time(9)
    ends_at: time = time(18)
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        PolicyRule.__post_init__(self)
        if self.starts_at >= self.ends_at:
            raise ValidationError("policy time window must be positive")
        try:
            ZoneInfo(self.timezone)
        except Exception as error:
            raise ValidationError("policy timezone is invalid") from error

    def matches(self, action: PolicyAction) -> bool:
        if not PolicyRule.matches(self, action):
            return False
        local = action.occurred_at.astimezone(ZoneInfo(self.timezone)).time().replace(tzinfo=None)
        return not self.starts_at <= local < self.ends_at


@dataclass(frozen=True, slots=True)
class RecipientAllowlistRule(PolicyRule):
    """Match if any recipient is outside an exact case-insensitive allowlist."""

    allowed: tuple[str, ...] = ()
    recipient_field: str = "recipients"

    def __post_init__(self) -> None:
        PolicyRule.__post_init__(self)
        if not self.allowed:
            raise ValidationError("recipient allowlist must not be empty")

    def matches(self, action: PolicyAction) -> bool:
        if not PolicyRule.matches(self, action):
            return False
        recipients = action.arguments.get(self.recipient_field, [])
        if isinstance(recipients, str):
            recipients = [recipients]
        if not isinstance(recipients, list):
            return True
        allowed = {item.casefold() for item in self.allowed}
        return any(
            not isinstance(item, str) or item.casefold() not in allowed for item in recipients
        )
