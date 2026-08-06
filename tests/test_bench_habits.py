from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_habits


def test_bench_habit_score_reports_planted_lapse_recall() -> None:
    bundle = create_bench_bundle(BenchConfig(6, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    score = score_bench_habits(bundle)
    assert score["app"] == "habits" and score["score"] == 1.0
    assert 0.0 <= score["mean_consistency"] <= 1.0
    assert score["lapse_span_count"] >= 1 and score["synthetic"] is True
