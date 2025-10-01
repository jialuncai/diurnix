from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase, LoopState, enforce_step_budget


def test_step_budget_stops_at_inclusive_limit() -> None:
    assert enforce_step_budget(LoopState(step_count=1), 2).phase is LoopPhase.PERCEIVE
    stopped = enforce_step_budget(LoopState(step_count=2), 2)
    assert stopped.phase is LoopPhase.STOPPED and stopped.stop_reason == "step budget exhausted"


def test_step_budget_rejects_negative_limit() -> None:
    with pytest.raises(ValidationError, match="cannot be negative"):
        enforce_step_budget(LoopState(), -1)
