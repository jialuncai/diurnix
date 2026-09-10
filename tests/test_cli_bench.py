from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_bench_emits_full_scorecard(capsys) -> None:
    assert main(["bench", "--seed", "9"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert tuple(payload["app_scores"]) == ("calendar", "habits", "inbox", "ledger", "tasks")
    assert payload["policy_violation_count"] == 0
    assert payload["budget_adherent"] is True and payload["replay_byte_equal"] is True
    assert payload["synthetic"] is True
