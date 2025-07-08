"""Deterministic pending approvals, scripted decisions, and escalation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    ESCALATED = "escalated"


@dataclass(frozen=True, slots=True)
class PendingApproval:
    approval_id: str
    call: ToolCall
    created_at: datetime
    expires_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_at: datetime | None = None
    actor: str | None = None
    reason: str | None = None
    escalation_level: int = 0

    def __post_init__(self) -> None:
        if self.expires_at <= self.created_at:
            raise ValidationError("approval expiry must follow creation")
        if self.escalation_level < 0:
            raise ValidationError("approval escalation level cannot be negative")
