from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, run_bench
from diurnix.codec import canonical_dumps
from diurnix.reports import (
    build_run_metadata,
    coverage_limitations,
    create_report_bundle,
)


def _bundle():
    start = datetime(2026, 10, 26, 9, tzinfo=UTC)
    config = BenchConfig(23, start)
    metadata = build_run_metadata(23, start, {"seed": 23, "offline": True})
    limitations = coverage_limitations(
        {
            "synthetic_data": True,
            "real_llm": False,
            "external_services": False,
            "torch_models": False,
        }
    )
    return create_report_bundle(metadata, run_bench(config), limitations, ())


def test_seeded_report_artifacts_are_byte_stable() -> None:
    first, second = _bundle(), _bundle()
    assert first.markdown.encode() == second.markdown.encode()
    assert first.html.encode() == second.html.encode()
    assert first.timeline_svg.encode() == second.timeline_svg.encode()


def test_seeded_report_manifest_is_canonical() -> None:
    assert canonical_dumps(_bundle().manifest) == canonical_dumps(_bundle().manifest)
