from __future__ import annotations

from diurnix.cli import main


def test_cli_returns_two_for_missing_session_file(capsys) -> None:
    assert main(["replay", "--path", "/definitely/missing/session.jsonl"]) == 2
    assert "diurnix:" in capsys.readouterr().err


def test_cli_returns_two_for_naive_start(capsys) -> None:
    assert main(["simulate", "--start", "2026-01-01T09:00:00"]) == 2
    assert "timezone-aware" in capsys.readouterr().err
