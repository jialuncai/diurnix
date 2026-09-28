"""Run all four applications and produce a self-contained report bundle."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from diurnix.bench import BenchConfig, run_bench, scorecard_to_dict
from diurnix.codec import canonical_dumps
from diurnix.factory import audit_bundle, bundle_manifest, generate_bundle
from diurnix.reports import build_run_metadata, coverage_limitations, create_report_bundle


def run(seed: int, output: Path) -> dict[str, object]:
    start = datetime(2026, 10, 26, 9, tzinfo=ZoneInfo("Asia/Shanghai"))
    synthetic = generate_bundle(seed, start)
    errors = audit_bundle(synthetic)
    if errors:
        raise RuntimeError("; ".join(errors))
    scorecard = run_bench(BenchConfig(seed, start))
    metadata = build_run_metadata(seed, start, {"seed": seed, "offline": True})
    limitations = coverage_limitations(
        {
            "synthetic_data": True,
            "real_llm": False,
            "external_services": False,
            "torch_models": False,
        }
    )
    reports = create_report_bundle(metadata, scorecard, limitations, ())
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.html").write_text(reports.html, encoding="utf-8")
    (output / "report.md").write_text(reports.markdown, encoding="utf-8")
    (output / "scorecard.json").write_text(
        canonical_dumps(scorecard_to_dict(scorecard)) + "\n", encoding="utf-8"
    )
    (output / "factory-manifest.json").write_text(
        canonical_dumps(bundle_manifest(synthetic)) + "\n", encoding="utf-8"
    )
    manifest = dict(reports.manifest)
    manifest["event_count"] = synthetic.event_count
    manifest["aggregate_score"] = scorecard.aggregate_score
    manifest["policy_violation_count"] = scorecard.policy_violation_count
    manifest["replay_byte_equal"] = scorecard.replay_byte_equal
    (output / "report-manifest.json").write_text(canonical_dumps(manifest) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=41)
    parser.add_argument("--output", type=Path, default=Path("persona-week-output"))
    args = parser.parse_args()
    print(canonical_dumps(run(args.seed, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
