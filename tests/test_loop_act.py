from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase, LoopState, record_action


def test_record_action_increments_step_and_preserves_receipt() -> None:
    state = record_action(LoopState(LoopPhase.ACT), {"status": "ok"})
    assert state.phase is LoopPhase.OBSERVE and state.step_count == 1
    assert state.receipts == ({"status": "ok"},)


def test_record_action_rejects_wrong_phase() -> None:
    with pytest.raises(ValidationError, match="not acting"):
        record_action(LoopState(), {})
