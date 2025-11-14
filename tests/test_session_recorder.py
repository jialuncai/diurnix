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


def test_recorder_copies_payload_at_append_boundary() -> None:
    payload = {"status": "pending"}
    recorder = SessionRecorder()
    entry = recorder.append("receipt.tool", "2026-10-30T09:00:00+08:00", payload)
    payload["status"] = "changed"
    assert entry.payload == {"status": "pending"}


def test_recorder_rejects_noncontiguous_initial_history() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.session import make_session_entry

    entry = make_session_entry(1, "event.user", "now", {})
    with pytest.raises(ValidationError, match="contiguous"):
        SessionRecorder((entry,))
