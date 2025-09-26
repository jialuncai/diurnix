from __future__ import annotations

from diurnix.loop import LoopPhase, LoopState, observe


def test_observe_closes_cycle_with_outcome() -> None:
    state = observe(LoopState(LoopPhase.OBSERVE, 1), {"result": 3})
    assert state.phase is LoopPhase.PERCEIVE and state.step_count == 1
    assert state.observations == ({"result": 3},)
