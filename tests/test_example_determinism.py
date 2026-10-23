from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_week(script: Path, output: Path) -> bytes:
    completed = subprocess.run(
        [sys.executable, str(script), "--seed", "41", "--output", str(output)],
        check=True,
        capture_output=True,
    )
    return completed.stdout


def test_full_week_stdout_and_every_artifact_are_byte_deterministic(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "persona_week" / "run.py"
    first = tmp_path / "first"
    second = tmp_path / "second"
    assert _run_week(script, first) == _run_week(script, second)
    first_files = {item.name: item.read_bytes() for item in first.iterdir()}
    second_files = {item.name: item.read_bytes() for item in second.iterdir()}
    assert first_files == second_files
    assert set(first_files) == {
        "factory-manifest.json",
        "report-manifest.json",
        "report.html",
        "report.md",
        "scorecard.json",
    }
