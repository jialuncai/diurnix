from __future__ import annotations

from diurnix.habits_app import habit_consistency_digest


def test_habit_digest_renders_measured_values() -> None:
    report = {
        "habit_count": 1,
        "synthetic": True,
        "habits": [{"habit": "阅读", "consistency": 0.8, "current_streak": 3}],
    }
    digest = habit_consistency_digest(report, {"recall": 1.0})
    assert digest.startswith("# 习惯一致性报告\n")
    assert "种植断档召回率: 100.00%" in digest
    assert "一致性 80.00%, 当前连续 3 天" in digest


def test_empty_habit_digest_is_explicit() -> None:
    digest = habit_consistency_digest({"habit_count": 0, "habits": []}, {"recall": 1.0})
    assert "习惯数: 0" in digest and "## 各习惯\n- 无" in digest
