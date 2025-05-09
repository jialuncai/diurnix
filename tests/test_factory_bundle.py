from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from diurnix.factory import SyntheticBundle
from diurnix.persona_factory import create_persona


def test_empty_synthetic_bundle_counts_domains() -> None:
    bundle = SyntheticBundle(1, create_persona(1), (), (), (), (), {})
    assert bundle.event_count == 0
    with pytest.raises(FrozenInstanceError):
        bundle.seed = 2  # type: ignore[misc]


def test_complete_bundle_contains_four_truth_labeled_domains() -> None:
    from datetime import UTC, datetime

    from diurnix.factory import generate_bundle

    bundle = generate_bundle(3, datetime(2026, 10, 1, 8, tzinfo=UTC))
    assert bundle.event_count == sum(
        len(stream) for stream in (bundle.inbox, bundle.calendar, bundle.ledger, bundle.habits)
    )
    assert set(bundle.ground_truth) == {"inbox", "calendar", "ledger", "habits"}
    assert bundle.ground_truth["ledger"]["anomaly_count"] > 0
    assert len(bundle.ground_truth["habits"]["lapse_ids"]) == 3
