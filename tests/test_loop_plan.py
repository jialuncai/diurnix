from __future__ import annotations

from diurnix.loop import LoopPhase, LoopState, attach_plan
from diurnix.plans import Plan, PlanStep, ValueType


def test_attach_plan_advances_to_act() -> None:
    plan = Plan("plan", (PlanStep("now", "clock.now", {}, {}, {"x": ValueType.ANY}),))
    state = attach_plan(LoopState(LoopPhase.PLAN), plan)
    assert state.phase is LoopPhase.ACT and state.plan is plan
