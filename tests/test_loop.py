from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase, LoopState, transition


def test_loop_follows_explicit_phase_cycle() -> None:
    state = LoopState()
    for phase in (LoopPhase.PLAN, LoopPhase.ACT, LoopPhase.OBSERVE, LoopPhase.PERCEIVE):
        state = transition(state, phase)
    assert state.phase is LoopPhase.PERCEIVE and state.step_count == 1


def test_loop_rejects_phase_skips() -> None:
    with pytest.raises(ValidationError, match="invalid"):
        transition(LoopState(), LoopPhase.ACT)
