from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_calendar


def test_bench_calendar_score_reports_recall_and_proposals() -> None:
    bundle = create_bench_bundle(BenchConfig(4, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    score = score_bench_calendar(bundle)
    assert score["app"] == "calendar" and score["score"] == 1.0
    assert 0.0 <= score["precision"] <= 1.0
    assert score["proposal_count"] == 1 and score["synthetic"] is True
