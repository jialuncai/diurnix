from __future__ import annotations

from diurnix.session import SessionRecorder, summarize_session


def test_session_summary_counts_kind_namespaces() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {})
    recorder.append("decision.policy", "t1", {})
    recorder.append("event.timer", "t2", {})
    assert summarize_session(recorder.entries) == {
        "entry_count": 3,
        "kind_counts": {"decision": 1, "event": 2},
        "first_recorded_at": "t0",
        "last_recorded_at": "t2",
    }


def test_empty_session_summary_has_no_time_bounds() -> None:
    assert summarize_session(())["first_recorded_at"] is None
    assert summarize_session(())["last_recorded_at"] is None
