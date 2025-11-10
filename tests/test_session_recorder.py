from __future__ import annotations

from diurnix.session import SessionRecorder


def test_session_recorder_assigns_contiguous_sequences() -> None:
    recorder = SessionRecorder()
    first = recorder.append("event.user", "2026-10-30T09:00:00+08:00", {"text": "hello"})
    second = recorder.append("decision.route", "2026-10-30T09:00:01+08:00", {"intent": "inbox"})
    assert (first.sequence, second.sequence) == (0, 1)
    assert recorder.entries == (first, second)


def test_empty_session_has_empty_byte_stream() -> None:
    assert SessionRecorder().to_jsonl_bytes() == b""
