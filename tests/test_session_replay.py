from __future__ import annotations

from diurnix.session import SessionRecorder, SessionReplayer


def test_session_replayer_reconstructs_reducer_state() -> None:
    recorder = SessionRecorder()
    recorder.append("counter.add", "t0", {"amount": 2})
    recorder.append("counter.add", "t1", {"amount": 3})
    total = SessionReplayer(recorder.entries).replay(
        lambda state, entry: state + int(entry.payload["amount"]), 0
    )
    assert total == 5


def test_replay_emits_live_bytes_unchanged() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": "hello"})
    assert SessionReplayer(recorder.entries).replay_bytes() == recorder.to_jsonl_bytes()
