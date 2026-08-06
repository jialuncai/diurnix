"""End-to-end synthetic persona benchmark harness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from diurnix.errors import ValidationError
from diurnix.factory import SyntheticBundle, generate_bundle


@dataclass(frozen=True, slots=True)
class BenchConfig:
    seed: int
    start: datetime
    max_task_minutes: int = 120
    max_task_count: int = 4

    def __post_init__(self) -> None:
        if self.seed < 0:
            raise ValidationError("bench seed cannot be negative")
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValidationError("bench start must be timezone-aware")
        if self.max_task_minutes < 0 or self.max_task_count < 0:
            raise ValidationError("bench task budgets cannot be negative")


def create_bench_bundle(config: BenchConfig) -> SyntheticBundle:
    return generate_bundle(config.seed, config.start)


def score_bench_inbox(bundle: SyntheticBundle) -> dict[str, object]:
    from diurnix.inbox_app import triage_inbox, triage_metrics

    results = triage_inbox(bundle.inbox)
    metrics = triage_metrics(bundle.inbox, results)
    return {
        "app": "inbox",
        "sample_count": metrics["sample_count"],
        "score": metrics["accuracy"],
        "ambiguous_count": 0,
        "synthetic": True,
    }


def score_bench_calendar(bundle: SyntheticBundle) -> dict[str, object]:
    from diurnix.calendar_app import calendar_conflict_metrics, propose_conflict_resolutions

    metrics = calendar_conflict_metrics(bundle.calendar)
    proposals = propose_conflict_resolutions(bundle.calendar, bundle.persona)
    return {
        "app": "calendar",
        "sample_count": metrics["entry_count"],
        "score": metrics["recall"],
        "precision": metrics["precision"],
        "proposal_count": len(proposals),
        "synthetic": True,
    }


def score_bench_ledger(bundle: SyntheticBundle) -> dict[str, object]:
    from diurnix.ledger_app import anomaly_metrics, detect_ledger_anomalies

    findings = detect_ledger_anomalies(bundle.ledger)
    metrics = anomaly_metrics(bundle.ledger, findings)
    return {
        "app": "ledger",
        "sample_count": metrics["transaction_count"],
        "score": metrics["recall"],
        "precision": metrics["precision"],
        "finding_count": metrics["finding_count"],
        "synthetic": True,
    }
