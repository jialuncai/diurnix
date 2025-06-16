"""Declarative allow, deny, and approval policy decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from diurnix.errors import ValidationError
from diurnix.tools import SideEffect


class PolicyEffect(StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class PolicyAction:
    """Policy-relevant projection of a proposed tool invocation."""

    tool: str
    capabilities: tuple[str, ...]
    side_effect: SideEffect
    arguments: dict[str, Any]
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValidationError("policy action time must be timezone-aware")


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    effect: PolicyEffect
    rule_id: str
    reason: str
    redacted_arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PolicyRule:
    """Declarative rule with optional tool and capability selectors."""

    rule_id: str
    effect: PolicyEffect
    reason: str
    priority: int = 0
    tools: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        from diurnix.identifiers import validate_identifier

        validate_identifier(self.rule_id, label="rule_id")
        if not self.reason.strip():
            raise ValidationError("policy rule reason must not be blank")

    def matches(self, action: PolicyAction) -> bool:
        """Match every nonempty selector as a conjunction."""
        tool_match = not self.tools or action.tool in self.tools
        capability_match = not self.capabilities or bool(
            set(self.capabilities) & set(action.capabilities)
        )
        return tool_match and capability_match


class PolicyEngine:
    """Deterministic rule evaluator with an explicit default effect."""

    def __init__(
        self, rules: tuple[PolicyRule, ...], *, default_effect: PolicyEffect = PolicyEffect.DENY
    ) -> None:
        if len({rule.rule_id for rule in rules}) != len(rules):
            raise ValidationError("policy rule IDs must be unique")
        self.rules = rules
        self.default_effect = default_effect

    def decide(self, action: PolicyAction) -> PolicyDecision:
        """Return the highest-precedence matching decision."""
        matches = [rule for rule in self.rules if rule.matches(action)]
        if not matches:
            return PolicyDecision(
                self.default_effect, "default", "no policy rule matched", dict(action.arguments)
            )
        severity = {PolicyEffect.ALLOW: 0, PolicyEffect.ASK: 1, PolicyEffect.DENY: 2}
        selected = max(
            matches, key=lambda rule: (rule.priority, severity[rule.effect], rule.rule_id)
        )
        return PolicyDecision(
            selected.effect, selected.rule_id, selected.reason, dict(action.arguments)
        )
