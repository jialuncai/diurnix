from __future__ import annotations

from diurnix.integrity import bytes_checksum
from diurnix.session import SessionRecorder, session_manifest


def test_session_manifest_hashes_executed_stream() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": "synthetic"})
    manifest = session_manifest(recorder.entries, seed=41)
    assert manifest["stream_checksum"] == bytes_checksum(recorder.to_jsonl_bytes())
    assert manifest["entry_count"] == 1
    assert manifest["synthetic"] is True


def test_empty_session_manifest_is_deterministic() -> None:
    assert session_manifest((), 1) == session_manifest((), 1)
