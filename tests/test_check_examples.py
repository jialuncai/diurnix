from __future__ import annotations

from pathlib import Path

from scripts.check_examples import EXAMPLE_SPECS, verify_example

ROOT = Path(__file__).parents[1]


def test_example_check_inventory_matches_documented_directories() -> None:
    assert tuple(spec.name for spec in EXAMPLE_SPECS) == (
        "persona_day",
        "ledger_anomaly",
        "habit_streak",
        "persona_week",
    )
    assert all((ROOT / "examples" / spec.name / "README.md").is_file() for spec in EXAMPLE_SPECS)


def test_example_check_executes_and_counts_persona_day_artifacts() -> None:
    result = verify_example(ROOT, EXAMPLE_SPECS[0])
    assert result == {"name": "persona_day", "seed": 17, "artifact_count": 4, "kind": "persona.day"}
