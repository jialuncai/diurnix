from __future__ import annotations

import pytest

from diurnix.cli import COMMAND_NAMES, build_parser, main


def test_every_cli_command_has_nonempty_help() -> None:
    parser = build_parser()
    choices = next(action.choices for action in parser._actions if action.dest == "command")
    assert tuple(choices) == COMMAND_NAMES
    for _name, command in choices.items():
        assert command.description is not None or command.format_help().strip()


def test_unknown_cli_command_returns_argparse_exit_two(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["unknown-command"])
    assert caught.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_root_invocation_remains_a_successful_noop() -> None:
    assert main([]) == 0
