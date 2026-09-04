from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_triage_emits_measured_manifest(capsys) -> None:
    assert main(["triage", "--seed", "3"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "inbox.triage" and payload["synthetic"] is True
    assert payload["metrics"]["sample_count"] == 35
    assert payload["metrics"]["accuracy"] == 1.0
