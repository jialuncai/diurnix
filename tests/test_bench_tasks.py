from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_tasks


def test_bench_tasks_respect_configured_budgets() -> None:
    config = BenchConfig(
        7,
        datetime(2026, 10, 26, 9, tzinfo=UTC),
        max_task_minutes=60,
        max_task_count=2,
    )
    score = score_bench_tasks(create_bench_bundle(config), config)
    assert score["app"] == "tasks" and score["budget_adherent"] is True
    assert score["scheduled_count"] <= 2 and score["effort_minutes"] <= 60
    assert 0.0 <= score["score"] <= 1.0
