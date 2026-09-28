from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_habit_example_recovers_planted_lapse_and_writes_heatmap(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "habit_streak" / "run.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--seed", "31", "--output", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["kind"] == "habits.analysis"
    assert payload["synthetic"] is True
    assert payload["metrics"]["recall"] == 1.0
    assert payload["metrics"]["planted_count"] == 3
    assert (tmp_path / "heatmap.svg").read_text().startswith("<svg")
    assert "种植断档召回率" in (tmp_path / "habit-report.md").read_text()
