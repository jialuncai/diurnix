from __future__ import annotations

from diurnix.router import Intent, NumpyRouter, evaluate_router


def test_router_evaluation_labels_synthetic_measurements() -> None:
    items = (
        ("邮件 回复", Intent.INBOX),
        ("budget 账单", Intent.LEDGER),
        ("habit 每天", Intent.HABITS),
    )
    report = evaluate_router(NumpyRouter(), items)
    assert report["synthetic"] is True and report["sample_count"] == 3
    assert 0 <= report["accuracy"] <= 1
