from __future__ import annotations

from pathlib import Path

from diurnix.session import SessionFileRecorder, SessionRecorder


def _append_tail(recorder) -> None:
    recorder.append("decision.route", "t1", {"intent": "tasks"})
    recorder.append("receipt.tool", "t2", {"status": "succeeded"})


def test_crash_resumed_file_matches_uninterrupted_session(tmp_path: Path) -> None:
    live = SessionRecorder()
    live.append("event.user", "t0", {"text": "plan"})
    _append_tail(live)

    path = tmp_path / "session.jsonl"
    before_crash = SessionFileRecorder(path)
    before_crash.append("event.user", "t0", {"text": "plan"})
    after_restart = SessionFileRecorder(path)
    _append_tail(after_restart)
    assert path.read_bytes() == live.to_jsonl_bytes()
