"""Reusable declarative and conditional policy rule helpers."""

from __future__ import annotations

from dataclasses import dataclass

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
