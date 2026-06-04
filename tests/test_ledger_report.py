from __future__ import annotations

from diurnix.ledger_app import ledger_analysis_manifest, monthly_ledger_digest


def test_monthly_ledger_digest_renders_actual_summary() -> None:
    summary = {
        "transaction_count": 2,
        "total_spending": 25.0,
        "category_spending": {"groceries": 20.0, "transport": 5.0},
        "anomaly_count": 1,
        "synthetic": True,
    }
    digest = monthly_ledger_digest(summary)
    assert digest.startswith("# 家庭账本月报\n")
    assert "支出合计: 25.00" in digest and "- groceries: 20.00" in digest


def test_ledger_manifest_labels_empty_synthetic_analysis() -> None:
    manifest = ledger_analysis_manifest((), (), 9)
    assert manifest["synthetic"] is True
    assert manifest["summary"]["transaction_count"] == 0
    assert str(manifest["svg_checksum"]).startswith("sha256:")
