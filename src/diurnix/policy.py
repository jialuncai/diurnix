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
