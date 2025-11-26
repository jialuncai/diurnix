from __future__ import annotations

from pathlib import Path

from diurnix.session import SessionFileRecorder


def test_file_recorder_appends_and_reopens(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "session.jsonl"
    writer = SessionFileRecorder(path)
    writer.append("event.user", "t0", {"text": "hello"})
    reopened = SessionFileRecorder(path)
    reopened.append("decision.route", "t1", {"intent": "inbox"})
    assert tuple(entry.sequence for entry in reopened.entries) == (0, 1)


def test_file_recorder_does_not_create_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "session.jsonl"
    SessionFileRecorder(path)
    assert not path.exists()
