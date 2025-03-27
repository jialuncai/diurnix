"""Deterministic factory for synthetic personal configurations."""

from __future__ import annotations

from datetime import time

from diurnix.identifiers import stable_identifier
from diurnix.persona import Correspondent, HabitGoal, MerchantProfile, Persona, WorkHours
from diurnix.randomness import SeededRandom

_NAMES = ("林晨", "周宁", "陈曦", "方舟")
_TIMEZONES = ("Asia/Shanghai", "Asia/Tokyo", "Europe/Berlin", "America/New_York")


def create_persona(seed: int) -> Persona:
    """Create a complete synthetic persona without external data."""
    random = SeededRandom(seed)
    name = random.choice(_NAMES)
    zone = random.choice(_TIMEZONES)
    persona_id = stable_identifier("persona", {"seed": seed}, length=12)
    contacts = (
        Correspondent("同学甲", "classmate@example.test", "classmate"),
        Correspondent("邻居乙", "neighbor@example.test", "neighbor"),
        Correspondent("未知发件人", "unknown@example.test", "unknown", trusted=False),
    )
    merchants = (
        MerchantProfile("合成市场", "groceries", 42.0),
        MerchantProfile("合成地铁", "transport", 4.0),
        MerchantProfile("合成视频", "subscriptions", 18.0, recurring=True),
    )
    goals = (HabitGoal("晨间步行", 5, 7, 1), HabitGoal("阅读", 6, 21, 0))
    return Persona(persona_id, name, zone, WorkHours(time(9), time(18)), contacts, merchants, goals)
