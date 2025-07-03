"""Policy-gated deterministic in-process tool executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from diurnix.identifiers import stable_identifier
from diurnix.policy import PolicyAction, PolicyDecision, PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry
from diurnix.tool_calls import ToolCall


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


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """Bounded retry count and deterministic jitter range."""

    max_attempts: int = 1
    base_delay_seconds: float = 0.0
    jitter_seconds: float = 0.0

    def __post_init__(self) -> None:
        from diurnix.errors import ValidationError

        if self.max_attempts < 1 or self.max_attempts > 10:
            raise ValidationError("retry attempts must be from one to ten")
        if self.base_delay_seconds < 0 or self.jitter_seconds < 0:
            raise ValidationError("retry delays cannot be negative")


class Executor:
    """Invoke registry tools only after a policy decision."""

    def __init__(
        self, registry: ToolRegistry, policy: PolicyEngine, retry: RetryConfig | None = None
    ) -> None:
        self.registry = registry
        self.policy = policy
        self.retry = retry or RetryConfig()

    def execute(self, call: ToolCall, now: datetime) -> ExecutionReceipt:
        """Evaluate policy and return a receipt for every outcome."""
        spec = self.registry.require(call.tool)
        action = PolicyAction(call.tool, spec.capabilities, spec.side_effect, call.arguments, now)
        decision = self.policy.decide(action)
        receipt_id = stable_identifier(
            "receipt", {"call_id": call.call_id, "tool": call.tool, "time": now.isoformat()}
        )
        if decision.effect is PolicyEffect.DENY:
            return ExecutionReceipt(
                receipt_id, call.call_id, call.tool, ExecutionStatus.DENIED, now, now, 0, decision
            )
        if decision.effect is PolicyEffect.ASK:
            return ExecutionReceipt(
                receipt_id, call.call_id, call.tool, ExecutionStatus.PENDING, now, now, 0, decision
            )
        try:
            output = self.registry.invoke(call.tool, call.arguments)
        except Exception as error:
            return ExecutionReceipt(
                receipt_id,
                call.call_id,
                call.tool,
                ExecutionStatus.FAILED,
                now,
                now,
                1,
                decision,
                error=f"{type(error).__name__}: {error}",
            )
        return ExecutionReceipt(
            receipt_id,
            call.call_id,
            call.tool,
            ExecutionStatus.SUCCEEDED,
            now,
            now,
            1,
            decision,
            output=output,
        )
