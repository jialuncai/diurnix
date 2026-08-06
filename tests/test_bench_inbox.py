from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_inbox


def test_bench_inbox_score_uses_planted_labels() -> None:
    score = score_bench_inbox(
        create_bench_bundle(BenchConfig(3, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    )
    assert score["app"] == "inbox" and score["sample_count"] == 35
    assert score["score"] == 1.0 and score["synthetic"] is True
