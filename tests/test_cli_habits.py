from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_habits_emits_planted_lapse_metrics(capsys) -> None:
    assert main(["habits", "--seed", "6"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "habits.analysis" and payload["synthetic"] is True
    assert payload["metrics"]["planted_count"] == 3
    assert payload["metrics"]["recall"] == 1.0
