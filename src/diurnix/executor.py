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


class ToolTimeout(TimeoutError):
    """Signal that a deterministic adapter exceeded its configured deadline."""


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


@dataclass(slots=True)
class CancellationToken:
    cancelled: bool = False
    reason: str = "cancelled"

    def cancel(self, reason: str = "cancelled") -> None:
        self.cancelled = True
        self.reason = reason


class Executor:
    """Invoke registry tools only after a policy decision."""

    def __init__(
        self, registry: ToolRegistry, policy: PolicyEngine, retry: RetryConfig | None = None
    ) -> None:
        self.registry = registry
        self.policy = policy
        self.retry = retry or RetryConfig()
        self._idempotency: dict[str, ExecutionReceipt] = {}
        self._idempotency_inputs: dict[str, tuple[str, str]] = {}

    def execute(
        self,
        call: ToolCall,
        now: datetime,
        *,
        idempotency_key: str | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ExecutionReceipt:
        """Evaluate policy and return a receipt for every outcome."""
        spec = self.registry.require(call.tool)
        if idempotency_key is not None and idempotency_key in self._idempotency:
            from diurnix.codec import canonical_dumps
            from diurnix.errors import ValidationError

            fingerprint = (call.tool, canonical_dumps(call.arguments))
            if self._idempotency_inputs[idempotency_key] != fingerprint:
                raise ValidationError("idempotency key was reused for different input")
            return self._idempotency[idempotency_key]
        action = PolicyAction(call.tool, spec.capabilities, spec.side_effect, call.arguments, now)
        decision = self.policy.decide(action)
        receipt_id = stable_identifier(
            "receipt", {"call_id": call.call_id, "tool": call.tool, "time": now.isoformat()}
        )
        if cancellation is not None and cancellation.cancelled:
            return ExecutionReceipt(
                receipt_id,
                call.call_id,
                call.tool,
                ExecutionStatus.CANCELLED,
                now,
                now,
                0,
                decision,
                error=cancellation.reason,
                idempotency_key=idempotency_key,
            )
        if decision.effect is PolicyEffect.DENY:
            return ExecutionReceipt(
                receipt_id, call.call_id, call.tool, ExecutionStatus.DENIED, now, now, 0, decision
            )
        if decision.effect is PolicyEffect.ASK:
            return ExecutionReceipt(
                receipt_id, call.call_id, call.tool, ExecutionStatus.PENDING, now, now, 0, decision
            )
        output: Any = None
        error: Exception | None = None
        attempts = 0
        for attempt in range(1, self.retry.max_attempts + 1):
            attempts = attempt
            try:
                output = self.registry.invoke(call.tool, call.arguments)
                error = None
                break
            except ToolTimeout as caught:
                return ExecutionReceipt(
                    receipt_id,
                    call.call_id,
                    call.tool,
                    ExecutionStatus.TIMED_OUT,
                    now,
                    now,
                    attempts,
                    decision,
                    error=str(caught) or "tool timed out",
                    idempotency_key=idempotency_key,
                )
            except Exception as caught:
                error = caught
        if error is not None:
            return ExecutionReceipt(
                receipt_id,
                call.call_id,
                call.tool,
                ExecutionStatus.FAILED,
                now,
                now,
                attempts,
                decision,
                error=f"{type(error).__name__}: {error}",
            )
        receipt = ExecutionReceipt(
            receipt_id,
            call.call_id,
            call.tool,
            ExecutionStatus.SUCCEEDED,
            now,
            now,
            attempts,
            decision,
            output=output,
            idempotency_key=idempotency_key,
        )
        if idempotency_key is not None:
            from diurnix.codec import canonical_dumps

            self._idempotency[idempotency_key] = receipt
            self._idempotency_inputs[idempotency_key] = (call.tool, canonical_dumps(call.arguments))
        return receipt


def retry_delays(config: RetryConfig, seed: int) -> tuple[float, ...]:
    """Calculate planned delays without sleeping during offline execution."""
    from diurnix.randomness import SeededRandom

    random = SeededRandom(seed)
    result = []
    for attempt in range(1, config.max_attempts):
        jitter_units = random.integer(0, 1_000_001) / 1_000_000
        delay = config.base_delay_seconds * attempt + config.jitter_seconds * jitter_units
        result.append(round(delay, 6))
    return tuple(result)


def execute_batch(
    executor: Executor, calls: tuple[ToolCall, ...], now: datetime, *, stop_on_failure: bool = True
) -> tuple[ExecutionReceipt, ...]:
    """Execute in order and stop after the first non-success when requested."""
    receipts = []
    for call in calls:
        receipt = executor.execute(call, now, idempotency_key=call.call_id)
        receipts.append(receipt)
        if stop_on_failure and receipt.status is not ExecutionStatus.SUCCEEDED:
            break
    return tuple(receipts)


def execute_approved(executor: Executor, approval: object, now: datetime) -> ExecutionReceipt:
    """Invoke an approved pending call under a one-call allow policy."""
    from diurnix.approvals import ApprovalStatus, PendingApproval

    if not isinstance(approval, PendingApproval) or approval.status is not ApprovalStatus.APPROVED:
        from diurnix.errors import ValidationError

        raise ValidationError("approval record is not approved")
    original = executor.policy
    try:
        executor.policy = PolicyEngine((), default_effect=PolicyEffect.ALLOW)
        return executor.execute(
            approval.call, now, idempotency_key=f"approval:{approval.approval_id}"
        )
    finally:
        executor.policy = original


def receipt_from_dict(value: dict[str, Any]) -> ExecutionReceipt:
    """Decode a strict current-version execution receipt."""
    from diurnix.errors import ValidationError

    expected = {
        "schema_version",
        "receipt_id",
        "call_id",
        "tool",
        "status",
        "started_at",
        "finished_at",
        "attempts",
        "decision",
        "output",
        "error",
        "idempotency_key",
    }
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("execution receipt does not match schema")
    try:
        decision_value = value["decision"]
        decision = PolicyDecision(
            PolicyEffect(decision_value["effect"]),
            decision_value["rule_id"],
            decision_value["reason"],
            dict(decision_value["redacted_arguments"]),
        )
        return ExecutionReceipt(
            value["receipt_id"],
            value["call_id"],
            value["tool"],
            ExecutionStatus(value["status"]),
            datetime.fromisoformat(value["started_at"]),
            datetime.fromisoformat(value["finished_at"]),
            value["attempts"],
            decision,
            value["output"],
            value["error"],
            value["idempotency_key"],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid execution receipt payload") from error


def execution_metrics(receipts: tuple[ExecutionReceipt, ...]) -> dict[str, object]:
    """Count statuses and attempts, retaining zero-count status fields."""
    return {
        "receipt_count": len(receipts),
        "statuses": {
            status.value: sum(item.status is status for item in receipts)
            for status in ExecutionStatus
        },
        "attempt_count": sum(item.attempts for item in receipts),
        "denied_execution_count": sum(
            item.attempts > 0 and item.status is ExecutionStatus.DENIED for item in receipts
        ),
    }


def executor_checkpoint(executor: Executor) -> dict[str, Any]:
    """Encode successful idempotency state for crash recovery."""
    return {
        "schema_version": 1,
        "idempotency": [
            {
                "key": key,
                "input": list(executor._idempotency_inputs[key]),
                "receipt": receipt_to_dict(executor._idempotency[key]),
            }
            for key in sorted(executor._idempotency)
        ],
    }


def restore_executor_checkpoint(executor: Executor, value: dict[str, Any]) -> None:
    """Restore validated successful receipts into an empty executor cache."""
    from diurnix.errors import ValidationError

    if set(value) != {"schema_version", "idempotency"} or value.get("schema_version") != 1:
        raise ValidationError("executor checkpoint does not match schema")
    if executor._idempotency:
        raise ValidationError("executor idempotency cache is not empty")
    try:
        for item in value["idempotency"]:
            receipt = receipt_from_dict(item["receipt"])
            if (
                receipt.status is not ExecutionStatus.SUCCEEDED
                or receipt.idempotency_key != item["key"]
            ):
                raise ValidationError("checkpoint contains invalid idempotent receipt")
            executor._idempotency[item["key"]] = receipt
            executor._idempotency_inputs[item["key"]] = tuple(item["input"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid executor checkpoint payload") from error


def resume_batch(
    executor: Executor, calls: tuple[ToolCall, ...], now: datetime
) -> tuple[ExecutionReceipt, ...]:
    """Execute a batch using call IDs as recovery-safe idempotency keys."""
    return tuple(executor.execute(call, now, idempotency_key=call.call_id) for call in calls)
