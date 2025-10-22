"""Deterministic NumPy intent routing over synthetic events."""

from __future__ import annotations

import re
from enum import StrEnum

_TOKEN = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(item.casefold() for item in _TOKEN.findall(text))


class Intent(StrEnum):
    INBOX = "inbox"
    CALENDAR = "calendar"
    TASKS = "tasks"
    LEDGER = "ledger"
    HABITS = "habits"


_KEYWORDS = {
    Intent.INBOX: ("mail", "邮件", "回复"),
    Intent.CALENDAR: ("calendar", "日程", "会议"),
    Intent.TASKS: ("task", "任务", "计划"),
    Intent.LEDGER: ("budget", "账单", "消费"),
    Intent.HABITS: ("habit", "习惯", "打卡"),
}


def keyword_counts(text: str) -> dict[Intent, int]:
    lowered = text.casefold()
    return {
        intent: sum(lowered.count(word) for word in words) for intent, words in _KEYWORDS.items()
    }


def recurrence_score(text: str) -> float:
    cues = ("每天", "每周", "daily", "weekly", "routine", "习惯")
    return round(min(1.0, sum(cue in text.casefold() for cue in cues) / 2), 6)
