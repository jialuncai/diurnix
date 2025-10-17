from __future__ import annotations

import random

from diurnix.loop import LoopPhase, LoopState, enforce_step_budget


def test_seeded_loop_sequences_terminate_within_budget() -> None:
    source = random.Random(20261030)
    for _ in range(200):
        limit = source.randrange(0, 30)
        state = LoopState(step_count=0)
        while state.phase is not LoopPhase.STOPPED:
            state = LoopState(step_count=state.step_count + 1)
            state = enforce_step_budget(state, limit)
        assert state.step_count >= limit and state.step_count <= max(1, limit)
