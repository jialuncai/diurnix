from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import SessionRecorder, query_session


def _entries():
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {})
    recorder.append("decision.route", "t1", {})
    recorder.append("event.timer", "t2", {})
    return recorder.entries


def test_session_query_combines_range_and_kind_prefix() -> None:
    result = query_session(_entries(), kind_prefix="event.", start=1)
    assert tuple(entry.sequence for entry in result) == (2,)


def test_session_query_validates_ranges_and_clamps_stop() -> None:
    assert len(query_session(_entries(), stop=99)) == 3
    with pytest.raises(ValidationError, match="range"):
        query_session(_entries(), start=2, stop=1)
