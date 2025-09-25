from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase, LoopState, perceive


def test_perceive_appends_event_and_advances() -> None:
    original = LoopState()
    changed = perceive(original, {"text": "hello"})
    assert changed.phase is LoopPhase.PLAN and changed.observations == ({"text": "hello"},)
    assert original.observations == ()


def test_perceive_rejects_wrong_phase() -> None:
    with pytest.raises(ValidationError, match="not perceiving"):
        perceive(LoopState(LoopPhase.ACT), 1)
