from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopState, perceive
from diurnix.session import SessionRecorder, record_loop_state


def test_session_records_loop_checkpoint_facts() -> None:
    state = perceive(LoopState(), {"event": "synthetic"})
    recorder = SessionRecorder()
    entry = record_loop_state(recorder, "t0", state)
    assert entry.payload == {
        "phase": "plan",
        "step_count": 0,
        "observation_count": 1,
        "receipt_count": 0,
        "stop_reason": None,
    }


def test_session_loop_recording_rejects_other_objects() -> None:
    with pytest.raises(ValidationError, match="wrong type"):
        record_loop_state(SessionRecorder(), "t0", {})
