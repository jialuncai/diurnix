from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, run_bench


def test_bench_scorecard_covers_all_applications() -> None:
    scorecard = run_bench(BenchConfig(9, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    assert tuple(scorecard.app_scores) == ("inbox", "calendar", "tasks", "ledger", "habits")
    assert 0.0 <= scorecard.aggregate_score <= 1.0
    assert scorecard.synthetic is True


def test_bench_scorecard_enforces_runtime_invariants() -> None:
    scorecard = run_bench(BenchConfig(9, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    assert scorecard.budget_adherent is True
    assert scorecard.policy_violation_count == 0
    assert scorecard.replay_byte_equal is True
