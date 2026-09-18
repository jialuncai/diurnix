"""Run one synthetic persona day through triage, planning, and approval."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from diurnix.approvals import (
    ApprovalQueue,
    ApproverMode,
    ScriptedApprover,
    run_escalation_chain,
)
from diurnix.calendar_app import calendar_digest, propose_conflict_resolutions
from diurnix.codec import canonical_dumps
from diurnix.events import InboxLabel
from diurnix.factory import generate_bundle
from diurnix.inbox_app import daily_triage_digest, triage_inbox, triage_metrics
from diurnix.tasks_app import TaskStatus, build_daily_task_plan, daily_plan_to_dict, make_task
from diurnix.tool_calls import ToolCall


def run(seed: int, output: Path) -> dict[str, object]:
    start = datetime(2026, 10, 26, 9, tzinfo=ZoneInfo("Asia/Shanghai"))
    bundle = generate_bundle(seed, start)
    triage = triage_inbox(bundle.inbox)
    metrics = triage_metrics(bundle.inbox, triage)
    proposals = propose_conflict_resolutions(bundle.calendar, bundle.persona)

    actionable = tuple(
        message for message in bundle.inbox if message.planted_label is InboxLabel.ACTION_REQUIRED
    )[:4]
    tasks = tuple(
        make_task(
            f"day_{message.event_id}",
            message.subject,
            start,
            deadline=start + timedelta(days=1),
            importance=max(1, message.priority),
            effort_minutes=30,
            status=TaskStatus.NEXT,
        )
        for message in actionable
    )
    plan = build_daily_task_plan(
        tasks,
        bundle.calendar,
        bundle.persona,
        start.date(),
        start,
        max_tasks=3,
        max_effort_minutes=90,
    )

    queue = ApprovalQueue()
    pending = queue.submit(
        ToolCall("persona_day_schedule", "calendar.write", {"slot_count": len(plan.slots)}),
        start,
    )
    escalated = run_escalation_chain(
        queue,
        pending.approval_id,
        (ScriptedApprover("scripted-owner", ApproverMode.DEFER, 15),),
    )
    summary: dict[str, object] = {
        "schema_version": 1,
        "seed": seed,
        "synthetic": True,
        "inbox_accuracy": metrics["accuracy"],
        "calendar_proposal_count": len(proposals),
        "scheduled_task_count": len(plan.slots),
        "task_effort_minutes": plan.effort_minutes,
        "approval_status": escalated.status.value,
        "approval_level": escalated.escalation_level,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "inbox.md").write_text(
        daily_triage_digest(triage, start.date().isoformat()), encoding="utf-8"
    )
    (output / "calendar.md").write_text(calendar_digest(bundle.calendar), encoding="utf-8")
    (output / "task-plan.json").write_text(
        canonical_dumps(daily_plan_to_dict(plan)) + "\n", encoding="utf-8"
    )
    (output / "summary.json").write_text(canonical_dumps(summary) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output", type=Path, default=Path("persona-day-output"))
    args = parser.parse_args()
    print(canonical_dumps(run(args.seed, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
