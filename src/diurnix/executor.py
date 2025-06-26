"""Policy-gated deterministic in-process tool executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from diurnix.policy import PolicyDecision


class ExecutionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DENIED = "denied"
    PENDING = "pending"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True, slots=True)
class ExecutionReceipt:
    """Complete observable outcome for one attempted tool call."""

    receipt_id: str
    call_id: str
    tool: str
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime
    attempts: int
    decision: PolicyDecision
    output: Any = None
    error: str | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        from diurnix.errors import ValidationError

        if self.finished_at < self.started_at:
            raise ValidationError("receipt finish precedes start")
        if self.attempts < 0:
            raise ValidationError("receipt attempts cannot be negative")


def receipt_to_dict(receipt: ExecutionReceipt) -> dict[str, Any]:
    """Encode a receipt into its current versioned schema."""
    return {
        "schema_version": 1,
        "receipt_id": receipt.receipt_id,
        "call_id": receipt.call_id,
        "tool": receipt.tool,
        "status": receipt.status.value,
        "started_at": receipt.started_at.isoformat(),
        "finished_at": receipt.finished_at.isoformat(),
        "attempts": receipt.attempts,
        "decision": {
            "effect": receipt.decision.effect.value,
            "rule_id": receipt.decision.rule_id,
            "reason": receipt.decision.reason,
            "redacted_arguments": receipt.decision.redacted_arguments,
        },
        "output": receipt.output,
        "error": receipt.error,
        "idempotency_key": receipt.idempotency_key,
    }
