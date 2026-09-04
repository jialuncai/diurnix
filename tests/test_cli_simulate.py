from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_simulate_emits_seeded_bundle_summary(capsys) -> None:
    assert main(["simulate", "--seed", "11"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["seed"] == 11 and payload["event_count"] > 0
    assert payload["synthetic"] is True
    assert payload["ground_truth_checksum"].startswith("sha256:")


def test_cli_simulate_is_deterministic(capsys) -> None:
    main(["simulate", "--seed", "11"])
    first = capsys.readouterr().out
    main(["simulate", "--seed", "11"])
    assert capsys.readouterr().out == first
