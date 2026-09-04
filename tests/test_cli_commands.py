from __future__ import annotations

from diurnix.cli import COMMAND_NAMES, build_parser, main


def test_cli_exposes_every_requested_subcommand() -> None:
    parser = build_parser()
    choices = next(action.choices for action in parser._actions if action.dest == "command")
    assert tuple(choices) == COMMAND_NAMES


def test_cli_subcommand_stubs_return_success_during_incremental_setup() -> None:
    assert all(main([name]) == 0 for name in COMMAND_NAMES)


def test_cli_root_help_lists_every_command(capsys) -> None:
    import pytest

    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    output = capsys.readouterr().out
    assert all(name in output for name in COMMAND_NAMES)


def test_each_command_help_identifies_its_name(capsys) -> None:
    import pytest

    for name in COMMAND_NAMES:
        with pytest.raises(SystemExit) as caught:
            main([name, "--help"])
        assert caught.value.code == 0
        assert f"diurnix {name}" in capsys.readouterr().out
