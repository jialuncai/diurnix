from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_schedule_reports_planted_conflict_recall(capsys) -> None:
    assert main(["schedule", "--seed", "4"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "calendar.analysis"
    assert payload["metrics"]["recall"] == 1.0
    assert payload["proposal_count"] == 1
