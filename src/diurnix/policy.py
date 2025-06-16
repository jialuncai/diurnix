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
