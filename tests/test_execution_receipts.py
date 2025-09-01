from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.executor import ExecutionReceipt, ExecutionStatus
from diurnix.policy import PolicyDecision, PolicyEffect

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
DECISION = PolicyDecision(PolicyEffect.ALLOW, "allow", "allowed", {})


def test_execution_status_wire_values_are_exhaustive() -> None:
    assert [item.value for item in ExecutionStatus] == [
        "succeeded",
        "failed",
        "denied",
        "pending",
        "cancelled",
        "timed_out",
    ]


def test_receipt_preserves_correlated_outcome() -> None:
    receipt = ExecutionReceipt(
        "receipt_1",
        "call_1",
        "clock.now",
        ExecutionStatus.SUCCEEDED,
        NOW,
        NOW,
        1,
        DECISION,
        output={"now": NOW.isoformat()},
    )
    assert receipt.output == {"now": NOW.isoformat()}
    assert receipt.error is None


def test_receipt_validates_time_and_attempts() -> None:
    with pytest.raises(ValidationError, match="precedes"):
        ExecutionReceipt(
            "r", "c", "tool", ExecutionStatus.FAILED, NOW, NOW.replace(hour=7), 1, DECISION
        )
    with pytest.raises(ValidationError, match="negative"):
        ExecutionReceipt("r", "c", "tool", ExecutionStatus.FAILED, NOW, NOW, -1, DECISION)


def test_execution_receipt_dataclass_fields_are_exhaustive() -> None:
    from dataclasses import fields

    assert [field.name for field in fields(ExecutionReceipt)] == [
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
    ]
