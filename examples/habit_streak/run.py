"""Render a 30-day synthetic habit stream with a planted lapse."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from diurnix.codec import canonical_dumps
from diurnix.factory import generate_bundle
from diurnix.habits_app import (
    detect_lapse_spans,
    habit_analysis_manifest,
    habit_consistency_digest,
    habit_consistency_report,
    habit_heatmap_svg,
    lapse_recovery_metrics,
)


def run(seed: int, output: Path) -> dict[str, object]:
    start = datetime(2026, 10, 1, 9, tzinfo=ZoneInfo("Asia/Shanghai"))
    bundle = generate_bundle(seed, start)
    spans = detect_lapse_spans(bundle.habits)
    metrics = lapse_recovery_metrics(bundle.habits, spans)
    report = habit_consistency_report(bundle.habits, bundle.persona.habit_goals)
    manifest = habit_analysis_manifest(bundle.habits, report, seed)
    output.mkdir(parents=True, exist_ok=True)
    (output / "habit-report.md").write_text(
        habit_consistency_digest(report, metrics), encoding="utf-8"
    )
    (output / "heatmap.svg").write_text(habit_heatmap_svg(bundle.habits), encoding="utf-8")
    (output / "manifest.json").write_text(canonical_dumps(manifest) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--output", type=Path, default=Path("habit-streak-output"))
    args = parser.parse_args()
    print(canonical_dumps(run(args.seed, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
