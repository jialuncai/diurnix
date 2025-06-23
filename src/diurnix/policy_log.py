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


def decision_metrics(log: DecisionLog) -> dict[str, object]:
    """Count effects and rules without omitting zero-count effects."""
    from diurnix.policy import PolicyEffect

    effects = {
        effect.value: sum(record.decision.effect is effect for record in log.records)
        for effect in PolicyEffect
    }
    rules: dict[str, int] = {}
    for record in log.records:
        rules[record.decision.rule_id] = rules.get(record.decision.rule_id, 0) + 1
    return {"decision_count": len(log.records), "effects": effects, "rules": rules}


def decision_log_to_dict(log: DecisionLog) -> dict[str, object]:
    """Encode the complete immutable audit trail."""
    return {
        "schema_version": 1,
        "records": [
            {
                "sequence": record.sequence,
                "occurred_at": record.occurred_at.isoformat(),
                "action_tool": record.action_tool,
                "effect": record.decision.effect.value,
                "rule_id": record.decision.rule_id,
                "reason": record.decision.reason,
                "redacted_arguments": record.decision.redacted_arguments,
            }
            for record in log.records
        ],
    }


def decision_log_from_dict(value: dict[str, object]) -> DecisionLog:
    """Decode a strict current-version decision log."""
    from diurnix.policy import PolicyDecision, PolicyEffect
    from diurnix.redaction import contains_pii

    if set(value) != {"schema_version", "records"} or value.get("schema_version") != 1:
        raise ValidationError("decision log does not match schema")
    records = value.get("records")
    if not isinstance(records, list):
        raise ValidationError("decision records must be an array")
    log = DecisionLog()
    try:
        for expected_sequence, item in enumerate(records):
            if set(item) != {
                "sequence",
                "occurred_at",
                "action_tool",
                "effect",
                "rule_id",
                "reason",
                "redacted_arguments",
            }:
                raise ValidationError("decision record fields do not match schema")
            if item["sequence"] != expected_sequence:
                raise ValidationError("decision sequences must be contiguous")
            if contains_pii(item["redacted_arguments"]):
                raise ValidationError("decision log contains unredacted PII")
            decision = PolicyDecision(
                PolicyEffect(item["effect"]),
                item["rule_id"],
                item["reason"],
                dict(item["redacted_arguments"]),
            )
            log = log.append(
                datetime.fromisoformat(item["occurred_at"]), item["action_tool"], decision
            )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid decision log payload") from error
    return log
