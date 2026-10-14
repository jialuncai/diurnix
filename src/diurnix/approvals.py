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

    def history(self) -> tuple[PendingApproval, ...]:
        """Return every request in creation order, including resolved records."""
        return tuple(
            sorted(self._records.values(), key=lambda item: (item.created_at, item.approval_id))
        )


class ApproverMode(StrEnum):
    AUTO_ALLOW = "auto_allow"
    AUTO_DENY = "auto_deny"
    DEFER = "defer"


@dataclass(frozen=True, slots=True)
class ScriptedApprover:
    """Offline deterministic adapter for approval tests and examples."""

    name: str
    mode: ApproverMode
    latency_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip() or self.latency_seconds < 0:
            raise ValidationError("approver name and latency are invalid")

    def response(self, approval: PendingApproval) -> tuple[bool, str] | None:
        if self.mode is ApproverMode.DEFER:
            return None
        approved = self.mode is ApproverMode.AUTO_ALLOW
        return approved, "scripted allow" if approved else "scripted deny"


def apply_scripted_approver(
    queue: ApprovalQueue, approval_id: str, approver: ScriptedApprover
) -> PendingApproval:
    """Apply one scripted response at its simulated decision time."""
    record = queue.get(approval_id)
    if record is None:
        raise ValidationError(f"unknown approval: {approval_id}")
    response = approver.response(record)
    if response is None:
        return record
    approved, reason = response
    decided_at = record.created_at + timedelta(seconds=approver.latency_seconds)
    return queue.decide(approval_id, approved, decided_at, actor=approver.name, reason=reason)


def escalate(
    queue: ApprovalQueue, approval_id: str, now: datetime, *, actor: str
) -> PendingApproval:
    """Advance a pending approval to the next escalation level."""
    record = queue.get(approval_id)
    if record is None:
        raise ValidationError(f"unknown approval: {approval_id}")
    if record.status is not ApprovalStatus.PENDING:
        raise ValidationError("only pending approvals can escalate")
    changed = replace(
        record,
        status=ApprovalStatus.ESCALATED,
        decided_at=now,
        actor=actor,
        reason="escalated",
        escalation_level=record.escalation_level + 1,
    )
    queue._records[approval_id] = changed
    return changed


def run_escalation_chain(
    queue: ApprovalQueue, approval_id: str, approvers: tuple[ScriptedApprover, ...]
) -> PendingApproval:
    """Ask scripted approvers in order until one resolves or all defer."""
    record = queue.get(approval_id)
    if record is None:
        raise ValidationError(f"unknown approval: {approval_id}")
    elapsed = 0.0
    for approver in approvers:
        response = approver.response(record)
        elapsed += approver.latency_seconds
        if response is not None:
            approved, reason = response
            return queue.decide(
                approval_id,
                approved,
                record.created_at + timedelta(seconds=elapsed),
                actor=approver.name,
                reason=reason,
            )
    return escalate(
        queue, approval_id, record.created_at + timedelta(seconds=elapsed), actor="chain"
    )


def approval_metrics(queue: ApprovalQueue) -> dict[str, float | int]:
    """Calculate simulated latency and outcome rates over resolved history."""
    history = queue.history()
    resolved = [item for item in history if item.decided_at is not None]
    latencies: list[float] = []
    for item in resolved:
        if item.decided_at is not None:
            latencies.append((item.decided_at - item.created_at).total_seconds())
    return {
        "request_count": len(history),
        "resolved_count": len(resolved),
        "mean_latency_seconds": round(sum(latencies) / len(latencies), 6) if latencies else 0.0,
        "escalation_rate": round(
            sum(item.status is ApprovalStatus.ESCALATED for item in history) / len(history), 6
        )
        if history
        else 0.0,
    }


def approval_queue_to_dict(queue: ApprovalQueue) -> dict[str, object]:
    """Encode calls and every lifecycle field in creation order."""
    from diurnix.tool_calls import tool_call_to_dict

    return {
        "schema_version": 1,
        "approvals": [
            {
                "approval_id": item.approval_id,
                "call": tool_call_to_dict(item.call),
                "created_at": item.created_at.isoformat(),
                "expires_at": item.expires_at.isoformat(),
                "status": item.status.value,
                "decided_at": item.decided_at.isoformat() if item.decided_at else None,
                "actor": item.actor,
                "reason": item.reason,
                "escalation_level": item.escalation_level,
            }
            for item in queue.history()
        ],
    }


def approval_queue_from_dict(value: dict[str, object]) -> ApprovalQueue:
    """Restore a strict approval lifecycle checkpoint."""
    from diurnix.tool_calls import tool_call_from_dict

    if set(value) != {"schema_version", "approvals"} or value.get("schema_version") != 1:
        raise ValidationError("approval queue does not match schema")
    if not isinstance(value["approvals"], list):
        raise ValidationError("approvals must be an array")
    queue = ApprovalQueue()
    try:
        for item in value["approvals"]:
            record = PendingApproval(
                item["approval_id"],
                tool_call_from_dict(item["call"]),
                datetime.fromisoformat(item["created_at"]),
                datetime.fromisoformat(item["expires_at"]),
                ApprovalStatus(item["status"]),
                datetime.fromisoformat(item["decided_at"]) if item["decided_at"] else None,
                item["actor"],
                item["reason"],
                item["escalation_level"],
            )
            queue._records[record.approval_id] = record
            queue._call_ids.add(record.call.call_id)
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid approval queue payload") from error
    return queue


def approval_queue_manifest(queue: ApprovalQueue) -> dict[str, object]:
    """Return checksummed approval history and simulated metrics."""
    from diurnix.integrity import content_checksum

    encoded = approval_queue_to_dict(queue)
    return {
        "kind": "approval.queue",
        "schema_version": 1,
        "checksum": content_checksum(encoded),
        "metrics": approval_metrics(queue),
        "queue": encoded,
    }
