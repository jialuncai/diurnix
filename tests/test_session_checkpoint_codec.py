from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import (
    SessionRecorder,
    checkpoint_from_dict,
    checkpoint_session,
    checkpoint_to_dict,
)


def test_session_checkpoint_mapping_roundtrips() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {})
    checkpoint = checkpoint_session(recorder)
    assert checkpoint_from_dict(checkpoint_to_dict(checkpoint)) == checkpoint


def test_session_checkpoint_codec_is_strict() -> None:
    with pytest.raises(ValidationError, match="schema"):
        checkpoint_from_dict({"schema_version": 2})
