"""Execute every documented offline example and verify its artifact inventory."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ExampleSpec:
    name: str
    seed: int
    artifacts: tuple[str, ...]


EXAMPLE_SPECS = (
    ExampleSpec("persona_day", 17, ("calendar.md", "inbox.md", "summary.json", "task-plan.json")),
    ExampleSpec("ledger_anomaly", 23, ("manifest.json", "monthly-digest.md", "spending.svg")),
    ExampleSpec("habit_streak", 31, ("habit-report.md", "heatmap.svg", "manifest.json")),
    ExampleSpec(
        "persona_week",
        41,
        (
            "factory-manifest.json",
            "report-manifest.json",
            "report.html",
            "report.md",
            "scorecard.json",
        ),
    ),
)


def verify_example(root: Path, spec: ExampleSpec) -> dict[str, object]:
    """Run one example in a temporary output directory and check exact artifacts."""
    script = root / "examples" / spec.name / "run.py"
    if not script.is_file():
        raise RuntimeError(f"missing example script: {script}")
    with tempfile.TemporaryDirectory(prefix=f"diurnix-{spec.name}-") as temporary:
        output = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(script), "--seed", str(spec.seed), "--output", str(output)],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        actual = tuple(sorted(item.name for item in output.iterdir()))
        expected = tuple(sorted(spec.artifacts))
        if actual != expected:
            raise RuntimeError(f"{spec.name} artifacts differ: expected {expected}, got {actual}")
        return {
            "name": spec.name,
            "seed": spec.seed,
            "artifact_count": len(actual),
            "kind": payload.get("kind", "persona.day"),
        }


def main() -> int:
    root = Path(__file__).parents[1]
    results = [verify_example(root, spec) for spec in EXAMPLE_SPECS]
    print(json.dumps({"examples": results, "offline": True}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
