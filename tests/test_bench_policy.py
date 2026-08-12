from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, run_denied_action_probe


def test_denied_action_probe_never_invokes_implementation() -> None:
    result = run_denied_action_probe(BenchConfig(1, datetime(2026, 1, 1, tzinfo=UTC)), count=5)
    assert result == {
        "attempt_count": 5,
        "denied_count": 5,
        "implementation_calls": 0,
        "policy_violation_count": 0,
    }
