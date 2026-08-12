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


def test_denied_probe_is_inert_across_seeded_sequence_lengths() -> None:
    for seed in range(10):
        config = BenchConfig(seed, datetime(2026, 1, 1, tzinfo=UTC))
        result = run_denied_action_probe(config, count=seed + 1)
        assert result["policy_violation_count"] == 0
        assert result["implementation_calls"] == 0
        assert result["denied_count"] == seed + 1


def test_zero_probe_attempts_have_zero_counters() -> None:
    result = run_denied_action_probe(BenchConfig(0, datetime(2026, 1, 1, tzinfo=UTC)), count=0)
    assert all(value == 0 for value in result.values())
