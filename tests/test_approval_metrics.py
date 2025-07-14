from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.approvals import ApprovalQueue, approval_metrics, escalate
from diurnix.tool_calls import ToolCall

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_approval_metrics_use_simulated_decision_times() -> None:
    queue = ApprovalQueue()
    first = queue.submit(ToolCall("call_1", "mail.send", {}), NOW)
    second = queue.submit(ToolCall("call_2", "mail.send", {}), NOW)
    queue.decide(first.approval_id, True, NOW + timedelta(seconds=2), actor="user", reason="ok")
    escalate(queue, second.approval_id, NOW + timedelta(seconds=4), actor="lead")
    assert approval_metrics(queue) == {
        "request_count": 2,
        "resolved_count": 2,
        "mean_latency_seconds": 3.0,
        "escalation_rate": 0.5,
    }


def test_empty_approval_metrics_are_zero_safe() -> None:
    assert approval_metrics(ApprovalQueue()) == {
        "request_count": 0,
        "resolved_count": 0,
        "mean_latency_seconds": 0.0,
        "escalation_rate": 0.0,
    }
