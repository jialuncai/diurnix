from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, run_bench, scorecard_to_dict
from diurnix.codec import canonical_dumps


def test_seeded_scorecard_is_byte_deterministic() -> None:
    config = BenchConfig(17, datetime(2026, 10, 26, 9, tzinfo=UTC))
    first = canonical_dumps(scorecard_to_dict(run_bench(config)))
    second = canonical_dumps(scorecard_to_dict(run_bench(config)))
    assert first == second


def test_seeded_scorecard_has_no_policy_violations() -> None:
    scorecard = run_bench(BenchConfig(17, datetime(2026, 10, 26, 9, tzinfo=UTC)))
    assert scorecard.policy_violation_count == 0
    assert scorecard.budget_adherent and scorecard.replay_byte_equal
