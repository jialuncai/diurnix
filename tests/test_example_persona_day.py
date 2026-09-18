from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_persona_day_example_executes_measured_pipeline(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "persona_day" / "run.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--seed", "17", "--output", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["synthetic"] is True
    assert payload["inbox_accuracy"] == 1.0
    assert payload["approval_status"] == "escalated"
    assert payload["approval_level"] == 1
    assert payload["task_effort_minutes"] <= 90
    assert {item.name for item in tmp_path.iterdir()} == {
        "calendar.md",
        "inbox.md",
        "summary.json",
        "task-plan.json",
    }
