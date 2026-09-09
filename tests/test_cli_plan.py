from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_plan_respects_task_budgets(capsys) -> None:
    assert main(["plan", "--seed", "7", "--max-minutes", "60", "--max-tasks", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["app"] == "tasks" and payload["budget_adherent"] is True
    assert payload["effort_minutes"] <= 60 and payload["scheduled_count"] <= 2
