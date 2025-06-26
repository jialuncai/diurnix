from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionReceipt, ExecutionStatus, receipt_to_dict
from diurnix.policy import PolicyDecision, PolicyEffect

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_receipt_mapping_has_exhaustive_stable_shape() -> None:
    receipt = ExecutionReceipt(
        "receipt_1",
        "call_1",
        "clock.now",
        ExecutionStatus.SUCCEEDED,
        NOW,
        NOW,
        1,
        PolicyDecision(PolicyEffect.ALLOW, "read", "read allowed", {}),
        output={"now": "08:00"},
    )
    encoded = receipt_to_dict(receipt)
    assert list(encoded) == [
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
    ]
    assert encoded["decision"] == {
        "effect": "allow",
        "rule_id": "read",
        "reason": "read allowed",
        "redacted_arguments": {},
    }
