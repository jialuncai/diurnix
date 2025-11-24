from __future__ import annotations

import pytest

from diurnix.errors import IntegrityError
from diurnix.session import SessionRecorder, checkpoint_session, resume_session


def test_session_checkpoint_resumes_after_simulated_crash() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {"text": "before crash"})
    checkpoint = checkpoint_session(recorder)
    resumed = resume_session(recorder.to_jsonl_bytes(), checkpoint)
    resumed.append("event.timer", "t1", {"name": "after restart"})
    assert tuple(entry.sequence for entry in resumed.entries) == (0, 1)


def test_session_checkpoint_rejects_changed_stream() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {})
    checkpoint = checkpoint_session(recorder)
    with pytest.raises(IntegrityError, match="checksum"):
        resume_session(recorder.to_jsonl_bytes() + b" ", checkpoint)
