from __future__ import annotations

from diurnix.events import InboxLabel
from diurnix.inbox_app import TriageResult, daily_triage_digest


def test_daily_digest_has_stable_label_order() -> None:
    results = (
        TriageResult("m2", InboxLabel.FYI, 0.6, ()),
        TriageResult("m1", InboxLabel.ACTION_REQUIRED, 0.98, ("请确认",)),
    )
    digest = daily_triage_digest(results, "2026-10-30")
    assert digest.startswith("# 收件箱摘要 · 2026-10-30\n")
    assert digest.index("action_required") < digest.index("fyi") < digest.index("newsletter")
    assert "- m1" in digest


def test_empty_daily_digest_states_no_pending_items() -> None:
    digest = daily_triage_digest((), "2026-10-30")
    assert "共处理 0 封合成邮件" in digest and "## 待确认\n- 无" in digest
