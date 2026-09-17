from __future__ import annotations

import json

from diurnix.cli import main


def test_json_commands_emit_one_canonical_line(capsys) -> None:
    commands = (
        ["route", "--text", "budget"],
        ["simulate", "--seed", "2"],
        ["triage", "--seed", "2"],
        ["schedule", "--seed", "2"],
        ["budget", "--seed", "2"],
        ["habits", "--seed", "2"],
        ["plan", "--seed", "2"],
        ["act"],
        ["bench", "--seed", "2"],
        ["demo", "--seed", "2"],
    )
    for command in commands:
        assert main(command) == 0
        output = capsys.readouterr().out
        assert output.endswith("\n") and output.count("\n") == 1
        assert json.loads(output) is not None


def test_seeded_cli_json_is_reproducible(capsys) -> None:
    main(["bench", "--seed", "12"])
    first = capsys.readouterr().out
    main(["bench", "--seed", "12"])
    assert capsys.readouterr().out == first
