from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_ledger_example_emits_measured_digest_and_svg(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "ledger_anomaly" / "run.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--seed", "23", "--output", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["kind"] == "ledger.analysis"
    assert payload["synthetic"] is True
    assert payload["metrics"]["recall"] > 0
    assert payload["metrics"]["finding_count"] == payload["summary"]["anomaly_count"]
    assert (tmp_path / "spending.svg").read_text().startswith("<svg")
    assert (tmp_path / "monthly-digest.md").read_text().startswith("# 家庭账本月报")
