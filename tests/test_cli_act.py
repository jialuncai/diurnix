from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_act_emits_successful_policy_receipt(capsys) -> None:
    assert main(["act", "--value", "offline text"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "succeeded" and payload["attempts"] == 1
    assert payload["decision"]["effect"] == "allow"
    assert payload["output"] == {"echo": "offline text"}
