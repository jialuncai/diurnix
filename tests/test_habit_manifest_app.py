from __future__ import annotations

from diurnix.habits_app import habit_analysis_manifest


def test_empty_habit_manifest_has_reproducible_checksums() -> None:
    report = {"habit_count": 0, "habits": [], "synthetic": True}
    first = habit_analysis_manifest((), report, 3)
    assert first == habit_analysis_manifest((), report, 3)
    assert first["synthetic"] is True and first["metrics"]["recall"] == 1.0
    assert str(first["heatmap_checksum"]).startswith("sha256:")
