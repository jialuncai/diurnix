"""Command-line entry point for deterministic offline workflows."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from diurnix import __version__

COMMAND_NAMES = (
    "simulate",
    "route",
    "plan",
    "act",
    "replay",
    "diff",
    "triage",
    "schedule",
    "budget",
    "habits",
    "digest",
    "bench",
    "demo",
)


def _command_stub(args: argparse.Namespace) -> int:
    del args
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the root parser and every public subcommand."""
    parser = argparse.ArgumentParser(
        prog="diurnix",
        description="运行确定性, 离线的个人代理机制与日常应用。",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    for name in COMMAND_NAMES:
        command = subparsers.add_parser(name, help=f"运行 {name} 工作流")
        configure = globals().get(f"_configure_{name}")
        if callable(configure):
            configure(command)
        command.set_defaults(handler=globals().get(f"_cmd_{name}", _command_stub))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, execute one command, and return its exit status."""
    args = build_parser().parse_args(argv)
    handler = getattr(args, "handler", None)
    from diurnix.errors import DiurnixError

    if not callable(handler):
        return 0
    try:
        return int(handler(args))
    except (OSError, DiurnixError) as error:
        import sys

        print(f"diurnix: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


def _configure_route(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", required=True, help="待路由的字面文本")
    parser.add_argument("--ambiguity-band", type=float, default=0.15)


def _cmd_route(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.router import NumpyRouter, route_probabilities, route_to_dict

    result = NumpyRouter(args.ambiguity_band).route(args.text)
    payload = route_to_dict(result)
    payload["probabilities"] = {
        intent.value: probability for intent, probability in route_probabilities(result).items()
    }
    print(canonical_dumps(payload))
    return 0


def _add_seed_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--start", default="2026-10-26T09:00:00+08:00")


def _parse_start(value: str):
    from datetime import datetime

    from diurnix.errors import ValidationError

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValidationError("start must use ISO datetime format") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValidationError("start must be timezone-aware")
    return parsed


def _configure_simulate(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_simulate(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.factory import bundle_manifest, generate_bundle

    bundle = generate_bundle(args.seed, _parse_start(args.start))
    manifest = bundle_manifest(bundle)
    print(
        canonical_dumps(
            {
                "seed": bundle.seed,
                "persona_id": bundle.persona.persona_id,
                "event_count": bundle.event_count,
                "ground_truth_checksum": manifest["ground_truth_checksum"],
                "synthetic": True,
            }
        )
    )
    return 0


def _configure_triage(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_triage(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.factory import generate_bundle
    from diurnix.inbox_app import triage_inbox, triage_manifest

    bundle = generate_bundle(args.seed, _parse_start(args.start))
    results = triage_inbox(bundle.inbox)
    print(canonical_dumps(triage_manifest(bundle.inbox, results, args.seed)))
    return 0


def _configure_schedule(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_schedule(args: argparse.Namespace) -> int:
    from diurnix.calendar_app import calendar_analysis_manifest, propose_conflict_resolutions
    from diurnix.codec import canonical_dumps
    from diurnix.factory import generate_bundle

    bundle = generate_bundle(args.seed, _parse_start(args.start))
    proposals = propose_conflict_resolutions(bundle.calendar, bundle.persona)
    print(canonical_dumps(calendar_analysis_manifest(bundle.calendar, proposals, args.seed)))
    return 0


def _configure_budget(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_budget(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.factory import generate_bundle
    from diurnix.ledger_app import detect_ledger_anomalies, ledger_analysis_manifest

    bundle = generate_bundle(args.seed, _parse_start(args.start))
    findings = detect_ledger_anomalies(bundle.ledger)
    print(canonical_dumps(ledger_analysis_manifest(bundle.ledger, findings, args.seed)))
    return 0


def _configure_habits(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_habits(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.factory import generate_bundle
    from diurnix.habits_app import habit_analysis_manifest, habit_consistency_report

    bundle = generate_bundle(args.seed, _parse_start(args.start))
    report = habit_consistency_report(bundle.habits, bundle.persona.habit_goals)
    print(canonical_dumps(habit_analysis_manifest(bundle.habits, report, args.seed)))
    return 0


def _configure_plan(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)
    parser.add_argument("--max-minutes", type=int, default=120)
    parser.add_argument("--max-tasks", type=int, default=4)


def _cmd_plan(args: argparse.Namespace) -> int:
    from diurnix.bench import BenchConfig, create_bench_bundle, score_bench_tasks
    from diurnix.codec import canonical_dumps

    config = BenchConfig(
        args.seed,
        _parse_start(args.start),
        max_task_minutes=args.max_minutes,
        max_task_count=args.max_tasks,
    )
    print(canonical_dumps(score_bench_tasks(create_bench_bundle(config), config)))
    return 0


def _configure_act(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--value", default="hello")
    parser.add_argument("--at", default="2026-10-26T09:00:00+08:00")


def _cmd_act(args: argparse.Namespace) -> int:
    from diurnix.codec import canonical_dumps
    from diurnix.executor import Executor, receipt_to_dict
    from diurnix.policy import PolicyEffect, PolicyEngine
    from diurnix.registry import ToolRegistry
    from diurnix.tool_calls import ToolCall
    from diurnix.tools import ToolSpec

    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "loopback.echo",
            "Return the supplied offline value.",
            {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            },
            ("loopback.read",),
        ),
        lambda arguments: {"echo": arguments["value"]},
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ALLOW))
    receipt = executor.execute(
        ToolCall("cli_act", "loopback.echo", {"value": args.value}), _parse_start(args.at)
    )
    print(canonical_dumps(receipt_to_dict(receipt)))
    return 0


def _configure_replay(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", required=True)
    parser.add_argument("--seed", type=int, default=0)


def _cmd_replay(args: argparse.Namespace) -> int:
    from pathlib import Path

    from diurnix.codec import canonical_dumps
    from diurnix.session import SessionReplayer, recorder_from_jsonl_bytes, session_manifest

    content = Path(args.path).read_bytes()
    recorder = recorder_from_jsonl_bytes(content)
    replayed = SessionReplayer(recorder.entries).replay_bytes()
    payload = session_manifest(recorder.entries, args.seed)
    payload["byte_equal"] = replayed == content
    print(canonical_dumps(payload))
    return 0


def _configure_diff(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)


def _cmd_diff(args: argparse.Namespace) -> int:
    from pathlib import Path

    from diurnix.codec import canonical_dumps
    from diurnix.session import diff_sessions, difference_to_dict, recorder_from_jsonl_bytes

    left = recorder_from_jsonl_bytes(Path(args.left).read_bytes()).entries
    right = recorder_from_jsonl_bytes(Path(args.right).read_bytes()).entries
    differences = [difference_to_dict(item) for item in diff_sessions(left, right)]
    print(
        canonical_dumps(
            {"schema_version": 1, "difference_count": len(differences), "differences": differences}
        )
    )
    return 1 if differences else 0


def _configure_digest(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)
    parser.add_argument("--format", choices=("markdown", "html"), default="markdown")


def _cmd_digest(args: argparse.Namespace) -> int:
    from diurnix.bench import BenchConfig, run_bench
    from diurnix.reports import (
        build_run_metadata,
        coverage_limitations,
        create_report_bundle,
    )

    start = _parse_start(args.start)
    config = BenchConfig(args.seed, start)
    metadata = build_run_metadata(args.seed, start, {"seed": args.seed, "offline": True})
    limitations = coverage_limitations(
        {
            "synthetic_data": True,
            "real_llm": False,
            "external_services": False,
            "torch_models": False,
        }
    )
    bundle = create_report_bundle(metadata, run_bench(config), limitations, ())
    print(bundle.html if args.format == "html" else bundle.markdown, end="")
    return 0


def _configure_bench(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_bench(args: argparse.Namespace) -> int:
    from diurnix.bench import BenchConfig, run_bench, scorecard_to_dict
    from diurnix.codec import canonical_dumps

    scorecard = run_bench(BenchConfig(args.seed, _parse_start(args.start)))
    print(canonical_dumps(scorecard_to_dict(scorecard)))
    return 0


def _configure_demo(parser: argparse.ArgumentParser) -> None:
    _add_seed_arguments(parser)


def _cmd_demo(args: argparse.Namespace) -> int:
    from diurnix.approvals import (
        ApprovalQueue,
        ApproverMode,
        ScriptedApprover,
        apply_scripted_approver,
        approval_metrics,
    )
    from diurnix.bench import BenchConfig, run_bench, scorecard_to_dict
    from diurnix.codec import canonical_dumps
    from diurnix.executor import Executor, execute_approved
    from diurnix.policy import PolicyEffect, PolicyEngine
    from diurnix.registry import ToolRegistry
    from diurnix.tool_calls import ToolCall
    from diurnix.tools import SideEffect, ToolSpec

    start = _parse_start(args.start)
    scorecard = run_bench(BenchConfig(args.seed, start))
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "calendar.write",
            "Write to the synthetic calendar.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            ("calendar.write",),
            SideEffect.LOCAL,
        ),
        lambda arguments: {"scheduled": True, "arguments": arguments},
    )
    executor = Executor(registry, PolicyEngine((), default_effect=PolicyEffect.ASK))
    queue = ApprovalQueue()
    pending = queue.submit(ToolCall("demo_schedule", "calendar.write", {}), start)
    approved = apply_scripted_approver(
        queue, pending.approval_id, ScriptedApprover("demo-persona", ApproverMode.AUTO_ALLOW, 1)
    )
    receipt = execute_approved(executor, approved, start)
    print(
        canonical_dumps(
            {
                "schema_version": 1,
                "seed": args.seed,
                "synthetic": True,
                "scorecard": scorecard_to_dict(scorecard),
                "approval_metrics": approval_metrics(queue),
                "approved_action_status": receipt.status.value,
            }
        )
    )
    return 0
