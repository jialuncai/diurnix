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


def test_file_recorder_preserves_existing_byte_prefix(tmp_path: Path) -> None:
    path = tmp_path / "session.jsonl"
    writer = SessionFileRecorder(path)
    writer.append("event.user", "t0", {"text": "first"})
    prefix = path.read_bytes()
    writer.append("event.timer", "t1", {"timer": "next"})
    assert path.read_bytes().startswith(prefix)
    assert len(path.read_bytes()) > len(prefix)


def test_file_recorder_rejects_torn_terminal_line(tmp_path: Path) -> None:
    import pytest

    from diurnix.errors import ValidationError

    path = tmp_path / "session.jsonl"
    path.write_bytes(b'{"schema_version":1}')
    with pytest.raises(ValidationError, match="newline"):
        SessionFileRecorder(path)
