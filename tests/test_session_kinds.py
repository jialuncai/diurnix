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


def test_each_session_kind_is_a_dotted_namespace() -> None:
    for item in SessionRecordKind:
        namespace, name = item.value.split(".", maxsplit=1)
        assert namespace and name


def test_typed_records_roundtrip_through_jsonl() -> None:
    from diurnix.session import recorder_from_jsonl_bytes

    recorder = SessionRecorder()
    for kind in SessionRecordKind:
        record_session_item(recorder, kind, "t0", {"kind": kind.value})
    restored = recorder_from_jsonl_bytes(recorder.to_jsonl_bytes())
    assert restored.entries == recorder.entries
