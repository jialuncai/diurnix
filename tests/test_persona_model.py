from __future__ import annotations

from datetime import time

import pytest

from diurnix.errors import ValidationError
from diurnix.persona import (
    Correspondent,
    HabitGoal,
    MerchantProfile,
    Persona,
    WorkHours,
)


def persona(**changes: object) -> Persona:
    values: dict[str, object] = {
        "persona_id": "persona_1",
        "name": "林晨",
        "timezone": "Asia/Shanghai",
        "work_hours": WorkHours(time(9), time(17)),
        "correspondents": (Correspondent("Lin", "lin@example.test", "classmate"),),
        "merchants": (MerchantProfile("Market", "food", 30),),
        "habit_goals": (HabitGoal("walk", 5, 8),),
    }
    values.update(changes)
    return Persona(**values)  # type: ignore[arg-type]


def test_persona_collects_all_factory_dimensions() -> None:
    model = persona()
    assert model.persona_id == "persona_1"
    assert model.timezone == "Asia/Shanghai"
    assert len(model.correspondents) == len(model.merchants) == len(model.habit_goals) == 1


def test_persona_rejects_unknown_timezone_and_missing_dimensions() -> None:
    with pytest.raises(ValidationError, match="IANA"):
        persona(timezone="Mars/Base")
    with pytest.raises(ValidationError, match="merchants and habit"):
        persona(merchants=())


def test_persona_requires_unique_merchant_and_habit_names() -> None:
    market = MerchantProfile("Market", "food", 30)
    with pytest.raises(ValidationError, match="merchant names"):
        persona(merchants=(market, market))
    walk = HabitGoal("Walk", 5, 8)
    with pytest.raises(ValidationError, match="habit names"):
        persona(habit_goals=(walk, HabitGoal("walk", 2, 9)))
