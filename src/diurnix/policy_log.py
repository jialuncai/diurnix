"""Immutable audit trail for policy decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from diurnix.errors import ValidationError
from diurnix.policy import PolicyDecision


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    sequence: int
    occurred_at: datetime
    action_tool: str
    decision: PolicyDecision


@dataclass(frozen=True, slots=True)
class DecisionLog:
    records: tuple[DecisionRecord, ...] = ()

    def append(
        self, occurred_at: datetime, action_tool: str, decision: PolicyDecision
    ) -> DecisionLog:
        """Return a new log with the next contiguous sequence number."""
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValidationError("decision time must be timezone-aware")
        record = DecisionRecord(len(self.records), occurred_at, action_tool, decision)
        return DecisionLog((*self.records, record))
