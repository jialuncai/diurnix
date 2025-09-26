from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase, LoopState, stop_loop


def test_stop_loop_preserves_runtime_state() -> None:
    state = LoopState(LoopPhase.ACT, 2, ("seen",), receipts=("receipt",))
    stopped = stop_loop(state, "complete")
    assert stopped.phase is LoopPhase.STOPPED and stopped.stop_reason == "complete"
    assert stopped.observations == state.observations and stopped.receipts == state.receipts


def test_stop_loop_requires_reason() -> None:
    with pytest.raises(ValidationError, match="reason"):
        stop_loop(LoopState(), " ")
