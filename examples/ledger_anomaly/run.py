"""Analyze a planted synthetic ledger and emit a deterministic monthly digest."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from diurnix.codec import canonical_dumps
from diurnix.factory import generate_bundle
from diurnix.ledger_app import (
    detect_ledger_anomalies,
    ledger_analysis_manifest,
    ledger_svg,
    monthly_ledger_digest,
    monthly_ledger_summary,
)


def run(seed: int, output: Path) -> dict[str, object]:
    start = datetime(2026, 10, 1, 9, tzinfo=ZoneInfo("Asia/Shanghai"))
    transactions = generate_bundle(seed, start).ledger
    findings = detect_ledger_anomalies(transactions)
    summary = monthly_ledger_summary(transactions, findings)
    manifest = ledger_analysis_manifest(transactions, findings, seed)
    output.mkdir(parents=True, exist_ok=True)
    (output / "monthly-digest.md").write_text(monthly_ledger_digest(summary), encoding="utf-8")
    (output / "spending.svg").write_text(ledger_svg(summary), encoding="utf-8")
    (output / "manifest.json").write_text(canonical_dumps(manifest) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--output", type=Path, default=Path("ledger-anomaly-output"))
    args = parser.parse_args()
    print(canonical_dumps(run(args.seed, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
