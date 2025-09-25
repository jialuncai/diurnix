"""Explicit perceive-plan-act-observe runtime state machine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from diurnix.errors import ValidationError


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


def transition(state: LoopState, target: LoopPhase) -> LoopState:
    if target is LoopPhase.STOPPED:
        return LoopState(
            target, state.step_count, state.observations, state.stop_reason or "stopped"
        )
    if _ALLOWED.get(state.phase) is not target:
        raise ValidationError(f"invalid loop transition: {state.phase} to {target}")
    return LoopState(
        target, state.step_count + (target is LoopPhase.ACT), state.observations, state.stop_reason
    )


def perceive(state: LoopState, event: Any) -> LoopState:
    if state.phase is not LoopPhase.PERCEIVE:
        raise ValidationError("loop is not perceiving")
    return LoopState(
        LoopPhase.PLAN, state.step_count, (*state.observations, event), state.stop_reason
    )
