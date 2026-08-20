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


def test_timeline_svg_escapes_unknown_kind_text() -> None:
    class Hostile:
        kind = "<script>alert(1)</script>"

    svg = decision_timeline_svg((Hostile(),))
    assert "<script>" not in svg and "&lt;script&gt;" in svg


def test_empty_timeline_svg_is_self_contained() -> None:
    svg = decision_timeline_svg(())
    assert svg.endswith("</svg>") and 'height="50"' in svg
