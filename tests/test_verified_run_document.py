from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from diurnix.bench import BenchConfig, run_bench, scorecard_to_dict
from diurnix.codec import canonical_dumps


def test_documented_scorecard_is_canonical_output_of_the_seeded_run() -> None:
    document = (Path(__file__).parents[1] / "docs" / "verified-run.md").read_text(encoding="utf-8")
    matches = re.findall(r"```json\n([^\n]+)\n```", document)
    assert len(matches) == 1
    documented = json.loads(matches[0])
    start = datetime.fromisoformat("2026-10-26T09:00:00+08:00")
    actual = scorecard_to_dict(run_bench(BenchConfig(41, start)))
    assert documented == actual
    assert matches[0] == canonical_dumps(actual)
