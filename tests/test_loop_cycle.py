from __future__ import annotations

from diurnix.loop import LoopPhase, LoopState
from diurnix.loop_runtime import run_cycle
from diurnix.plans import Plan, PlanStep, ValueType


def test_run_cycle_returns_to_perceive_with_trace_values() -> None:
    plan = Plan("plan", (PlanStep("step", "clock.now", {}, {}, {"x": ValueType.ANY}),))
    state = run_cycle(LoopState(), "event", plan, "receipt", "observation")
    assert state.phase is LoopPhase.PERCEIVE and state.step_count == 1
    assert state.observations == ("event", "observation") and state.receipts == ("receipt",)
