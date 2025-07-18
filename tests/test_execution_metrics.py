from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionReceipt, ExecutionStatus, execution_metrics
from diurnix.policy import PolicyDecision, PolicyEffect

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
DECISION = PolicyDecision(PolicyEffect.ALLOW, "allow", "ok", {})


def test_execution_metrics_count_statuses_attempts_and_invariant() -> None:
    receipts = (
        ExecutionReceipt("r1", "c1", "a", ExecutionStatus.SUCCEEDED, NOW, NOW, 1, DECISION),
        ExecutionReceipt("r2", "c2", "b", ExecutionStatus.FAILED, NOW, NOW, 3, DECISION),
    )
    metrics = execution_metrics(receipts)
    assert metrics["receipt_count"] == 2
    assert metrics["attempt_count"] == 4
    assert metrics["statuses"]["succeeded"] == 1
    assert metrics["statuses"]["failed"] == 1
    assert metrics["denied_execution_count"] == 0


def test_empty_execution_metrics_retain_status_schema() -> None:
    metrics = execution_metrics(())
    assert set(metrics["statuses"]) == {status.value for status in ExecutionStatus}
    assert metrics["attempt_count"] == 0
