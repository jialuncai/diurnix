from __future__ import annotations

from datetime import UTC, datetime

from diurnix.executor import ExecutionReceipt, ExecutionStatus, execution_audit
from diurnix.policy import PolicyDecision, PolicyEffect


def test_execution_audit_reports_zero_policy_violations() -> None:
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    receipt = ExecutionReceipt(
        "receipt_1",
        "call_1",
        "mail.send",
        ExecutionStatus.DENIED,
        now,
        now,
        0,
        PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {}),
    )
    audit = execution_audit(
        (receipt,),
        {"request_count": 1, "resolved_count": 1, "mean_latency_seconds": 2.0},
    )
    assert audit["policy_violations"] == 0
    assert audit["safe"] is True
    assert audit["execution"]["statuses"]["denied"] == 1


def test_execution_audit_copies_approval_metrics() -> None:
    approvals = {"request_count": 0}
    audit = execution_audit((), approvals)
    audit["approvals"]["request_count"] = 2
    assert approvals == {"request_count": 0}
