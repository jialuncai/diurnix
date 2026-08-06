from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_ledger


def test_bench_ledger_score_uses_executed_findings() -> None:
    bundle = create_bench_bundle(BenchConfig(5, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    score = score_bench_ledger(bundle)
    assert score["app"] == "ledger" and score["sample_count"] == len(bundle.ledger)
    assert 0.0 <= score["score"] <= 1.0 and 0.0 <= score["precision"] <= 1.0
    assert score["finding_count"] > 0 and score["synthetic"] is True
