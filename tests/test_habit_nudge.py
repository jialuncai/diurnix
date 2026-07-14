from __future__ import annotations

from datetime import date

from diurnix.habits_app import StreakSummary, habit_nudge, schedule_routine
from diurnix.persona import HabitGoal


def test_habit_nudge_reflects_current_streak_and_schedule() -> None:
    schedule = schedule_routine(HabitGoal("阅读", 5, 8), date(2026, 10, 30), (), "Asia/Shanghai")
    text = habit_nudge(StreakSummary("阅读", 4, 7, 10, 1), schedule)
    assert text == "阅读: 08:00 继续当前 4 天连续记录。"


def test_habit_nudge_handles_missing_slot() -> None:
    text = habit_nudge(StreakSummary("阅读", 0, 2, 3, 0), None)
    assert "没有可用时段" in text and "手动选择" in text
