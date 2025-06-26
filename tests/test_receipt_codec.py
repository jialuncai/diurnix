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


def test_receipt_checksum_is_stable_for_equal_outcomes() -> None:
    from diurnix.integrity import content_checksum

    decision = PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {"to": "[EMAIL]"})
    left = ExecutionReceipt(
        "receipt_1", "call_1", "mail.send", ExecutionStatus.DENIED, NOW, NOW, 0, decision
    )
    right = ExecutionReceipt(
        "receipt_1", "call_1", "mail.send", ExecutionStatus.DENIED, NOW, NOW, 0, decision
    )
    assert content_checksum(receipt_to_dict(left)) == content_checksum(receipt_to_dict(right))


def test_receipt_wire_contains_no_unredacted_decision_argument() -> None:
    from diurnix.codec import canonical_dumps

    decision = PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {"to": "[EMAIL]"})
    receipt = ExecutionReceipt(
        "receipt_1", "call_1", "mail.send", ExecutionStatus.DENIED, NOW, NOW, 0, decision
    )
    text = canonical_dumps(receipt_to_dict(receipt))
    assert "[EMAIL]" in text
    assert "example.test" not in text
