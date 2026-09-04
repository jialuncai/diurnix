from __future__ import annotations

from diurnix.cli import COMMAND_NAMES, build_parser, main


def test_cli_exposes_every_requested_subcommand() -> None:
    parser = build_parser()
    choices = next(action.choices for action in parser._actions if action.dest == "command")
    assert tuple(choices) == COMMAND_NAMES


def test_cli_subcommand_stubs_return_success_during_incremental_setup() -> None:
    assert all(main([name]) == 0 for name in COMMAND_NAMES)
