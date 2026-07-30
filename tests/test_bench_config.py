from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.bench import BenchConfig, create_bench_bundle
from diurnix.errors import ValidationError

START = datetime(2026, 10, 26, 9, tzinfo=UTC)


def test_bench_config_generates_complete_bundle() -> None:
    bundle = create_bench_bundle(BenchConfig(7, START))
    assert bundle.seed == 7 and bundle.event_count > 0
    assert set(bundle.ground_truth) == {"inbox", "calendar", "ledger", "habits"}


def test_bench_config_validates_seed_time_and_budgets() -> None:
    with pytest.raises(ValidationError, match="seed"):
        BenchConfig(-1, START)
    with pytest.raises(ValidationError, match="timezone-aware"):
        BenchConfig(1, datetime(2026, 1, 1))
    with pytest.raises(ValidationError, match="budgets"):
        BenchConfig(1, START, max_task_minutes=-1)


def test_same_bench_config_produces_same_bundle() -> None:
    config = BenchConfig(19, START)
    assert create_bench_bundle(config) == create_bench_bundle(config)


def test_different_bench_seeds_change_bundle_identity() -> None:
    assert (
        create_bench_bundle(BenchConfig(1, START)).persona.persona_id
        != create_bench_bundle(BenchConfig(2, START)).persona.persona_id
    )
