from __future__ import annotations

from datetime import date

import pytest

from diurnix.errors import ValidationError
from diurnix.habits_app import (
    routine_schedule_from_dict,
    routine_schedule_to_dict,
    schedule_routine,
)
from diurnix.persona import HabitGoal


def _schedule():
    result = schedule_routine(HabitGoal("阅读", 5, 8), date(2026, 10, 30), (), "Asia/Shanghai")
    assert result is not None
    return result


def test_routine_schedule_mapping_roundtrips() -> None:
    schedule = _schedule()
    assert routine_schedule_from_dict(routine_schedule_to_dict(schedule)) == schedule


def test_routine_schedule_codec_rejects_extensions() -> None:
    encoded = routine_schedule_to_dict(_schedule())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        routine_schedule_from_dict(encoded)
