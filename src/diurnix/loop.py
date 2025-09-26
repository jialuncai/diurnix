"""Explicit perceive-plan-act-observe runtime state machine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from diurnix.errors import ValidationError
from diurnix.plans import Plan


class LoopPhase(StrEnum):
    PERCEIVE = "perceive"
    PLAN = "plan"
    ACT = "act"
    OBSERVE = "observe"
    STOPPED = "stopped"


_ALLOWED = {
    LoopPhase.PERCEIVE: LoopPhase.PLAN,
    LoopPhase.PLAN: LoopPhase.ACT,
    LoopPhase.ACT: LoopPhase.OBSERVE,
    LoopPhase.OBSERVE: LoopPhase.PERCEIVE,
}


@dataclass(frozen=True, slots=True)
class LoopState:
    phase: LoopPhase = LoopPhase.PERCEIVE
    step_count: int = 0
    observations: tuple[Any, ...] = ()
    stop_reason: str | None = None
    plan: Plan | None = None
    receipts: tuple[Any, ...] = ()


def transition(state: LoopState, target: LoopPhase) -> LoopState:
    if target is LoopPhase.STOPPED:
        return LoopState(
            target, state.step_count, state.observations, state.stop_reason or "stopped", state.plan
        )
    if _ALLOWED.get(state.phase) is not target:
        raise ValidationError(f"invalid loop transition: {state.phase} to {target}")
    return LoopState(
        target,
        state.step_count + (target is LoopPhase.ACT),
        state.observations,
        state.stop_reason,
        state.plan,
    )


def perceive(state: LoopState, event: Any) -> LoopState:
    if state.phase is not LoopPhase.PERCEIVE:
        raise ValidationError("loop is not perceiving")
    return LoopState(
        LoopPhase.PLAN,
        state.step_count,
        (*state.observations, event),
        state.stop_reason,
        state.plan,
    )


def attach_plan(state: LoopState, plan: Plan) -> LoopState:
    """Attach a validated plan and advance to action."""
    if state.phase is not LoopPhase.PLAN:
        raise ValidationError("loop is not planning")
    return LoopState(LoopPhase.ACT, state.step_count, state.observations, state.stop_reason, plan)


def record_action(state: LoopState, receipt: Any) -> LoopState:
    """Record one action outcome and advance to observation."""
    if state.phase is not LoopPhase.ACT:
        raise ValidationError("loop is not acting")
    return LoopState(
        LoopPhase.OBSERVE,
        state.step_count + 1,
        state.observations,
        state.stop_reason,
        state.plan,
        (*state.receipts, receipt),
    )
