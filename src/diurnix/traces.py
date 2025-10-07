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


def trace_to_dict(trace: LoopTrace) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "entries": [
            {
                "sequence": e.sequence,
                "phase": e.phase.value,
                "occurred_at": e.occurred_at.isoformat(),
                "payload": e.payload,
            }
            for e in trace.entries
        ],
    }


def trace_from_dict(value: dict[str, Any]) -> LoopTrace:
    if set(value) != {"schema_version", "entries"} or value.get("schema_version") != 1:
        raise ValidationError("trace does not match schema")
    trace = LoopTrace()
    try:
        for expected, item in enumerate(value["entries"]):
            if item["sequence"] != expected:
                raise ValidationError("trace sequence is not contiguous")
            trace = trace.append(
                LoopPhase(item["phase"]),
                datetime.fromisoformat(item["occurred_at"]),
                dict(item["payload"]),
            )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid trace payload") from error
    return trace


def trace_manifest(trace: LoopTrace) -> dict[str, Any]:
    from diurnix.integrity import content_checksum

    encoded = trace_to_dict(trace)
    return {
        "kind": "loop.trace",
        "schema_version": 1,
        "entry_count": len(trace.entries),
        "checksum": content_checksum(encoded),
        "trace": encoded,
    }
