from __future__ import annotations

from diurnix.session import SessionRecorder, SessionRecordKind, record_session_item


def test_session_record_kinds_have_stable_values() -> None:
    assert tuple(item.value for item in SessionRecordKind) == (
        "event.input",
        "decision.policy",
        "receipt.tool",
        "observation.tool",
        "checkpoint.runtime",
    )


def test_typed_session_recording_preserves_kind() -> None:
    recorder = SessionRecorder()
    entry = record_session_item(recorder, SessionRecordKind.DECISION, "t0", {"effect": "ask"})
    assert entry.kind == "decision.policy"
