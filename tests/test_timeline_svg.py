from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.reports import decision_timeline_svg
from diurnix.session import SessionRecorder


def test_timeline_svg_renders_session_order() -> None:
    recorder = SessionRecorder()
    recorder.append("event.user", "t0", {})
    recorder.append("decision.policy", "t1", {})
    svg = decision_timeline_svg(recorder.entries)
    assert svg.index("0: event.user") < svg.index("1: decision.policy")
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')


def test_timeline_svg_validates_width() -> None:
    with pytest.raises(ValidationError, match="small"):
        decision_timeline_svg((), width=100)
