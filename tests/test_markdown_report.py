from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchScorecard
from diurnix.reports import build_run_metadata, render_markdown_report


def test_markdown_report_embeds_scores_and_metadata() -> None:
    metadata = build_run_metadata(3, datetime(2026, 1, 1, tzinfo=UTC), {"seed": 3})
    scorecard = BenchScorecard(3, {"inbox": 1.0, "ledger": 0.75}, 0.875, True, 0, True)
    report = render_markdown_report(metadata, scorecard, ("仅限合成数据。",))
    assert report.startswith("# diurnix 合成运行报告\n")
    assert "- inbox: 1.0000" in report and "- aggregate: 0.8750" in report
    assert metadata.config_checksum in report and "policy_violations: 0" in report


def test_markdown_report_is_deterministic() -> None:
    metadata = build_run_metadata(3, datetime(2026, 1, 1, tzinfo=UTC), {})
    scorecard = BenchScorecard(3, {}, 0.0, True, 0, True)
    assert render_markdown_report(metadata, scorecard, ()) == render_markdown_report(
        metadata, scorecard, ()
    )
