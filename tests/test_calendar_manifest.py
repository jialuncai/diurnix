from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import (
    calendar_manifest,
    calendar_week_with_conflict,
    with_travel_constraints,
)


def test_calendar_manifest_is_reproducible_and_complete() -> None:
    entries = with_travel_constraints(
        calendar_week_with_conflict(create_persona(3), 8, date(2026, 10, 26)), 19
    )
    manifest = calendar_manifest(entries, seed=8)
    assert manifest == calendar_manifest(entries, seed=8)
    assert manifest["factory_version"] == 1
    assert manifest["events"]["count"] == len(entries)
    assert manifest["ground_truth"]["entry_count"] == len(entries)
