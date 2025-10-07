"""Deterministic runtime traces for loop replay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from diurnix.errors import ValidationError
from diurnix.loop import LoopPhase


@dataclass(frozen=True, slots=True)
class TraceEntry:
    sequence: int
    phase: LoopPhase
    occurred_at: datetime
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValidationError("trace sequence cannot be negative")
        if self.occurred_at.tzinfo is None:
            raise ValidationError("trace time must be timezone-aware")


@dataclass(frozen=True, slots=True)
class LoopTrace:
    entries: tuple[TraceEntry, ...] = ()

    def append(self, phase: LoopPhase, at: datetime, payload: dict[str, Any]) -> LoopTrace:
        return LoopTrace((*self.entries, TraceEntry(len(self.entries), phase, at, dict(payload))))
