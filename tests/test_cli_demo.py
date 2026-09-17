from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_demo_runs_factory_apps_approval_and_action(capsys) -> None:
    assert main(["demo", "--seed", "10"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["synthetic"] is True and payload["seed"] == 10
    assert payload["scorecard"]["policy_violation_count"] == 0
    assert payload["approval_metrics"]["request_count"] == 1
    assert payload["approved_action_status"] == "succeeded"
