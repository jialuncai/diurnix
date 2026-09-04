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
    return int(handler(args)) if callable(handler) else 0


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
