from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_persona_week_example_executes_all_apps_and_report_bundle(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "persona_week" / "run.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--seed", "41", "--output", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["kind"] == "report.bundle"
    assert payload["policy_violation_count"] == 0
    assert payload["replay_byte_equal"] is True
    assert payload["event_count"] > 100
    assert (tmp_path / "report.html").read_text().startswith("<!doctype html>")
    scorecard = json.loads((tmp_path / "scorecard.json").read_text())
    assert set(scorecard["app_scores"]) == {"calendar", "habits", "inbox", "ledger", "tasks"}
