from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchScorecard
from diurnix.reports import build_run_metadata, render_html_report


def test_html_report_is_self_contained() -> None:
    metadata = build_run_metadata(2, datetime(2026, 1, 1, tzinfo=UTC), {})
    scorecard = BenchScorecard(2, {"inbox": 1.0}, 1.0, True, 0, True)
    html = render_html_report(metadata, scorecard, ("合成数据。",), "<svg></svg>")
    assert html.startswith("<!doctype html>") and html.endswith("</html>")
    assert "<style>" in html and "<svg></svg>" in html
    assert "http://" not in html and "https://" not in html


def test_html_report_embeds_scorecard_values() -> None:
    metadata = build_run_metadata(2, datetime(2026, 1, 1, tzinfo=UTC), {})
    scorecard = BenchScorecard(2, {"ledger": 0.75}, 0.75, True, 0, True)
    html = render_html_report(metadata, scorecard, (), "")
    assert "<th>ledger</th><td>0.7500</td>" in html
    assert "<th>aggregate</th><td>0.7500</td>" in html
