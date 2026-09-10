from __future__ import annotations

import json
from pathlib import Path

from diurnix.cli import main
from diurnix.session import SessionRecorder


def test_cli_replay_verifies_byte_equality(tmp_path: Path, capsys) -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": "hello"})
    path = tmp_path / "session.jsonl"
    path.write_bytes(recorder.to_jsonl_bytes())
    assert main(["replay", "--path", str(path), "--seed", "4"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "session.recording" and payload["entry_count"] == 1
    assert payload["byte_equal"] is True and payload["seed"] == 4
