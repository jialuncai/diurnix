from __future__ import annotations

from datetime import date

from diurnix.calendar_app import calendar_digest
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_calendar_digest_reports_executed_conflicts() -> None:
    entries = calendar_week_with_conflict(create_persona(9), 9, date(2026, 10, 26))
    digest = calendar_digest(entries)
    assert digest.startswith("# 日程检查\n")
    assert "重叠冲突: 1" in digest
    assert "calendar_conflict_9_0" in digest


def test_empty_calendar_digest_is_explicit() -> None:
    digest = calendar_digest(())
    assert "日程数: 0" in digest and "重叠冲突: 0" in digest and "- 无" in digest
