from __future__ import annotations

from datetime import UTC, datetime

from diurnix.approvals import ApprovalQueue, approval_queue_to_dict
from diurnix.codec import canonical_dumps
from diurnix.tool_calls import ToolCall


def test_approval_queue_mapping_contains_pending_call() -> None:
    queue = ApprovalQueue()
    record = queue.submit(
        ToolCall("call_1", "mail.send", {"to": "[EMAIL]"}), datetime(2026, 10, 30, 8, tzinfo=UTC)
    )
    encoded = approval_queue_to_dict(queue)
    assert encoded["schema_version"] == 1
    assert encoded["approvals"][0]["approval_id"] == record.approval_id
    assert encoded["approvals"][0]["status"] == "pending"
    assert "example.test" not in canonical_dumps(encoded)


def test_empty_approval_queue_has_stable_golden_json() -> None:
    assert canonical_dumps(approval_queue_to_dict(ApprovalQueue())) == (
        '{"approvals":[],"schema_version":1}'
    )


def test_approval_queue_checkpoint_roundtrips_resolved_history() -> None:
    from diurnix.approvals import approval_queue_from_dict

    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), now)
    queue.decide(record.approval_id, False, now, actor="user", reason="no")
    restored = approval_queue_from_dict(approval_queue_to_dict(queue))
    assert restored.history() == queue.history()


def test_approval_queue_checkpoint_rejects_schema_drift() -> None:
    import pytest

    from diurnix.approvals import approval_queue_from_dict
    from diurnix.errors import ValidationError

    with pytest.raises(ValidationError, match="match schema"):
        approval_queue_from_dict({"schema_version": 2, "approvals": []})
