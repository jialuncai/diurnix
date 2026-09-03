from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchScorecard
from diurnix.integrity import content_checksum
from diurnix.reports import build_run_metadata, create_report_bundle


def test_report_bundle_manifest_hashes_every_artifact() -> None:
    metadata = build_run_metadata(5, datetime(2026, 1, 1, tzinfo=UTC), {"seed": 5})
    scorecard = BenchScorecard(5, {"inbox": 1.0}, 1.0, True, 0, True)
    bundle = create_report_bundle(metadata, scorecard, ("合成数据。",), ())
    assert bundle.manifest["markdown_checksum"] == content_checksum(bundle.markdown)
    assert bundle.manifest["html_checksum"] == content_checksum(bundle.html)
    assert bundle.manifest["timeline_checksum"] == content_checksum(bundle.timeline_svg)
    assert bundle.manifest["synthetic"] is True


def test_report_bundle_is_deterministic() -> None:
    metadata = build_run_metadata(5, datetime(2026, 1, 1, tzinfo=UTC), {})
    scorecard = BenchScorecard(5, {}, 0.0, True, 0, True)
    assert create_report_bundle(metadata, scorecard, (), ()) == create_report_bundle(
        metadata, scorecard, (), ()
    )
