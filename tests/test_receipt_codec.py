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


def test_receipt_mapping_roundtrips_every_outcome_field() -> None:
    from diurnix.executor import receipt_from_dict

    receipt = ExecutionReceipt(
        "receipt_1",
        "call_1",
        "clock.now",
        ExecutionStatus.SUCCEEDED,
        NOW,
        NOW,
        2,
        PolicyDecision(PolicyEffect.ALLOW, "read", "allowed", {}),
        output={"value": 3},
        idempotency_key="key",
    )
    assert receipt_from_dict(receipt_to_dict(receipt)) == receipt


def test_receipt_decoder_rejects_schema_drift() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.executor import receipt_from_dict

    valid = receipt_to_dict(
        ExecutionReceipt(
            "receipt_1",
            "call_1",
            "clock.now",
            ExecutionStatus.DENIED,
            NOW,
            NOW,
            0,
            PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {}),
        )
    )
    with pytest.raises(ValidationError, match="match schema"):
        receipt_from_dict({**valid, "extra": True})


def test_receipt_decoder_rejects_unknown_status_and_bad_time() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.executor import receipt_from_dict

    valid = receipt_to_dict(
        ExecutionReceipt(
            "receipt_1",
            "call_1",
            "clock.now",
            ExecutionStatus.DENIED,
            NOW,
            NOW,
            0,
            PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {}),
        )
    )
    with pytest.raises(ValidationError, match="invalid execution"):
        receipt_from_dict({**valid, "status": "unknown"})
    with pytest.raises(ValidationError, match="invalid execution"):
        receipt_from_dict({**valid, "started_at": "not-a-time"})


def test_receipt_decoder_applies_time_order_validation() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.executor import receipt_from_dict

    valid = receipt_to_dict(
        ExecutionReceipt(
            "receipt_1",
            "call_1",
            "clock.now",
            ExecutionStatus.DENIED,
            NOW,
            NOW,
            0,
            PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {}),
        )
    )
    with pytest.raises(ValidationError, match="precedes"):
        receipt_from_dict({**valid, "finished_at": "2026-10-30T07:00:00+00:00"})
