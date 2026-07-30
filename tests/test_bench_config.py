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
