from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_budget_emits_anomaly_and_spending_metrics(capsys) -> None:
    assert main(["budget", "--seed", "5"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "ledger.analysis" and payload["synthetic"] is True
    assert payload["metrics"]["truth_count"] == 6
    assert payload["summary"]["total_spending"] > 0
