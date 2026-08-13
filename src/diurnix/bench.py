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


def score_bench_habits(bundle: SyntheticBundle) -> dict[str, object]:
    from diurnix.habits_app import (
        detect_lapse_spans,
        habit_consistency_report,
        lapse_recovery_metrics,
    )

    spans = detect_lapse_spans(bundle.habits)
    metrics = lapse_recovery_metrics(bundle.habits, spans)
    report = habit_consistency_report(bundle.habits, bundle.persona.habit_goals)
    consistency = [float(item["consistency"]) for item in report["habits"]]
    return {
        "app": "habits",
        "sample_count": len(bundle.habits),
        "score": metrics["recall"],
        "mean_consistency": round(sum(consistency) / len(consistency), 6) if consistency else 0.0,
        "lapse_span_count": len(spans),
        "synthetic": True,
    }


def score_bench_tasks(bundle: SyntheticBundle, config: BenchConfig) -> dict[str, object]:
    from datetime import timedelta

    from diurnix.events import InboxLabel
    from diurnix.tasks_app import TaskStatus, build_daily_task_plan, make_task

    action_messages = tuple(
        message for message in bundle.inbox if message.planted_label is InboxLabel.ACTION_REQUIRED
    )[:6]
    tasks = tuple(
        make_task(
            f"task_{message.event_id}",
            message.subject,
            config.start,
            deadline=config.start + timedelta(days=1),
            importance=max(1, message.priority),
            effort_minutes=30,
            status=TaskStatus.NEXT,
        )
        for message in action_messages
    )
    plan = build_daily_task_plan(
        tasks,
        bundle.calendar,
        bundle.persona,
        config.start.date(),
        config.start,
        max_tasks=config.max_task_count,
        max_effort_minutes=config.max_task_minutes,
    )
    score = round(len(plan.slots) / len(tasks), 6) if tasks else 1.0
    return {
        "app": "tasks",
        "sample_count": len(tasks),
        "score": score,
        "scheduled_count": len(plan.slots),
        "effort_minutes": plan.effort_minutes,
        "budget_adherent": plan.effort_minutes <= config.max_task_minutes,
        "synthetic": True,
    }


def run_denied_action_probe(config: BenchConfig, *, count: int = 1) -> dict[str, object]:
    from diurnix.executor import ExecutionStatus, Executor
    from diurnix.policy import PolicyEffect, PolicyEngine
    from diurnix.registry import ToolRegistry
    from diurnix.tool_calls import ToolCall
    from diurnix.tools import SideEffect, ToolSpec

    executions = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "mail.send",
            "Synthetic denied mail sender.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            ("mail.send",),
            SideEffect.EXTERNAL,
        ),
        lambda arguments: executions.append(arguments),
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.DENY))
    receipts = tuple(
        executor.execute(ToolCall(f"denied_{index}", "mail.send", {}), config.start)
        for index in range(count)
    )
    violations = sum(receipt.status is not ExecutionStatus.DENIED for receipt in receipts)
    return {
        "attempt_count": count,
        "denied_count": sum(receipt.status is ExecutionStatus.DENIED for receipt in receipts),
        "implementation_calls": len(executions),
        "policy_violation_count": violations,
    }


def record_bench_sections(config: BenchConfig, sections: tuple[dict[str, object], ...]) -> bytes:
    from diurnix.session import SessionRecorder

    recorder = SessionRecorder()
    recorded_at = config.start.isoformat()
    recorder.append("event.bench", recorded_at, {"seed": config.seed})
    for section in sections:
        recorder.append(f"observation.{section['app']}", recorded_at, dict(section))
    return recorder.to_jsonl_bytes()


@dataclass(frozen=True, slots=True)
class BenchScorecard:
    seed: int
    app_scores: dict[str, float]
    aggregate_score: float
    budget_adherent: bool
    policy_violation_count: int
    replay_byte_equal: bool
    synthetic: bool = True


def run_bench(config: BenchConfig) -> BenchScorecard:
    bundle = create_bench_bundle(config)
    sections = (
        score_bench_inbox(bundle),
        score_bench_calendar(bundle),
        score_bench_tasks(bundle, config),
        score_bench_ledger(bundle),
        score_bench_habits(bundle),
    )
    app_scores = {str(section["app"]): float(section["score"]) for section in sections}
    aggregate = round(sum(app_scores.values()) / len(app_scores), 6)
    policy = run_denied_action_probe(config, count=5)
    live = record_bench_sections(config, sections)
    replay = record_bench_sections(config, sections)
    return BenchScorecard(
        config.seed,
        app_scores,
        aggregate,
        bool(sections[2]["budget_adherent"]),
        int(policy["policy_violation_count"]),
        live == replay,
    )
