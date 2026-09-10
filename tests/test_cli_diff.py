from __future__ import annotations

import json
from pathlib import Path

from diurnix.cli import main
from diurnix.session import SessionRecorder


def _write(path: Path, text: str) -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": text})
    path.write_bytes(recorder.to_jsonl_bytes())


def test_cli_diff_returns_zero_for_equal_sessions(tmp_path: Path, capsys) -> None:
    left, right = tmp_path / "left", tmp_path / "right"
    _write(left, "same")
    _write(right, "same")
    assert main(["diff", "--left", str(left), "--right", str(right)]) == 0
    assert json.loads(capsys.readouterr().out)["difference_count"] == 0


def test_cli_diff_returns_one_for_changed_sessions(tmp_path: Path, capsys) -> None:
    left, right = tmp_path / "left", tmp_path / "right"
    _write(left, "first")
    _write(right, "second")
    assert main(["diff", "--left", str(left), "--right", str(right)]) == 1
    assert json.loads(capsys.readouterr().out)["difference_count"] == 1
