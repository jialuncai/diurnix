from __future__ import annotations

from diurnix.session import SessionRecorder, diff_sessions


def _record(text: str):
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": text})
    return recorder.entries


def test_session_diff_is_empty_for_equal_traces() -> None:
    assert diff_sessions(_record("same"), _record("same")) == ()


def test_session_diff_reports_changes_and_missing_tail() -> None:
    left = _record("left")
    right_recorder = SessionRecorder(_record("right"))
    right_recorder.append("decision.route", "t1", {"intent": "tasks"})
    differences = diff_sessions(left, right_recorder.entries)
    assert tuple(item.sequence for item in differences) == (0, 1)
    assert differences[1].left_checksum is None
