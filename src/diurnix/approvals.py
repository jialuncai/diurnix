"""Deterministic pending approvals, scripted decisions, and escalation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
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


class ApprovalQueue:
    """Mutable queue whose records remain immutable snapshots."""

    def __init__(self) -> None:
        self._records: dict[str, PendingApproval] = {}
        self._call_ids: set[str] = set()

    def submit(
        self, call: ToolCall, now: datetime, *, ttl: timedelta = timedelta(hours=1)
    ) -> PendingApproval:
        """Create one pending request for a call identity."""
        from diurnix.identifiers import stable_identifier

        if ttl <= timedelta(0):
            raise ValidationError("approval TTL must be positive")
        if call.call_id in self._call_ids:
            raise ValidationError(f"approval already exists for call: {call.call_id}")
        approval_id = stable_identifier(
            "approval", {"call_id": call.call_id, "created_at": now.isoformat()}
        )
        record = PendingApproval(approval_id, call, now, now + ttl)
        self._records[approval_id] = record
        self._call_ids.add(call.call_id)
        return record

    def get(self, approval_id: str) -> PendingApproval | None:
        return self._records.get(approval_id)

    def pending(self) -> tuple[PendingApproval, ...]:
        return tuple(
            sorted(
                (item for item in self._records.values() if item.status is ApprovalStatus.PENDING),
                key=lambda item: (item.created_at, item.approval_id),
            )
        )

    def expire(self, now: datetime) -> tuple[PendingApproval, ...]:
        """Expire pending requests at their inclusive deadline."""
        expired = []
        for approval_id, record in tuple(self._records.items()):
            if record.status is ApprovalStatus.PENDING and now >= record.expires_at:
                changed = replace(
                    record,
                    status=ApprovalStatus.EXPIRED,
                    decided_at=now,
                    actor="system",
                    reason="approval expired",
                )
                self._records[approval_id] = changed
                expired.append(changed)
        return tuple(expired)

    def decide(
        self, approval_id: str, approved: bool, now: datetime, *, actor: str, reason: str
    ) -> PendingApproval:
        """Resolve exactly one still-pending approval."""
        record = self._records.get(approval_id)
        if record is None:
            raise ValidationError(f"unknown approval: {approval_id}")
        if record.status is not ApprovalStatus.PENDING:
            raise ValidationError("approval is already resolved")
        if now > record.expires_at:
            self.expire(now)
            raise ValidationError("approval has expired")
        if not actor.strip() or not reason.strip():
            raise ValidationError("approval actor and reason must not be blank")
        changed = replace(
            record,
            status=ApprovalStatus.APPROVED if approved else ApprovalStatus.DENIED,
            decided_at=now,
            actor=actor,
            reason=reason,
        )
        self._records[approval_id] = changed
        return changed
