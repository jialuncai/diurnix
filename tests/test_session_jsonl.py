from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import SessionRecorder, recorder_from_jsonl_bytes


def test_session_jsonl_roundtrips_unicode_records() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "2026-10-30T09:00:00+08:00", {"text": "今日计划"})
    assert recorder_from_jsonl_bytes(recorder.to_jsonl_bytes()).entries == recorder.entries


def test_session_jsonl_requires_terminal_newline() -> None:
    with pytest.raises(ValidationError, match="newline"):
        recorder_from_jsonl_bytes(b"{}")


def test_same_session_inputs_produce_identical_bytes() -> None:
    def record() -> bytes:
        recorder = SessionRecorder()
        recorder.append("event.user", "2026-10-30T09:00:00+08:00", {"z": 1, "a": "值"})
        recorder.append("decision.policy", "2026-10-30T09:00:01+08:00", {"allow": True})
        return recorder.to_jsonl_bytes()

    assert record() == record()


def test_session_jsonl_reports_corrupt_line_number() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "now", {})
    damaged = recorder.to_jsonl_bytes() + b"not-json\n"
    with pytest.raises(ValidationError, match="line 2"):
        recorder_from_jsonl_bytes(damaged)
