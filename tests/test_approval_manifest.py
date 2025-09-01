from __future__ import annotations

from datetime import UTC, datetime

from diurnix.approvals import ApprovalQueue, approval_queue_manifest
from diurnix.integrity import content_checksum
from diurnix.tool_calls import ToolCall


def test_approval_manifest_covers_history_and_metrics() -> None:
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    queue = ApprovalQueue()
    record = queue.submit(ToolCall("call_1", "mail.send", {}), now)
    queue.decide(record.approval_id, True, now, actor="user", reason="ok")
    manifest = approval_queue_manifest(queue)
    assert manifest["kind"] == "approval.queue"
    assert manifest["checksum"] == content_checksum(manifest["queue"])
    assert manifest["metrics"]["resolved_count"] == 1


def test_empty_approval_manifest_is_reproducible() -> None:
    assert approval_queue_manifest(ApprovalQueue()) == approval_queue_manifest(ApprovalQueue())
