from __future__ import annotations

from datetime import date

from diurnix.persona_factory import create_persona
from diurnix.synthetic_habits import (
    generate_habit_stream,
    habit_manifest,
    plant_habit_lapse,
)


def test_habit_manifest_covers_exact_events_and_truth() -> None:
    persona = create_persona(3)
    events = generate_habit_stream(persona, 6, date(2026, 10, 1))
    events = plant_habit_lapse(events, persona.habit_goals[0].name, date(2026, 10, 10))
    manifest = habit_manifest(events, seed=6)
    assert manifest == habit_manifest(events, seed=6)
    assert manifest["events"]["count"] == len(events)
    assert len(manifest["ground_truth"]["lapse_ids"]) == 3
    assert str(manifest["events"]["checksum"]).startswith("sha256:")
