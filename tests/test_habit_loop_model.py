from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.habits_app import HabitLoop


def test_habit_loop_keeps_explicit_mechanism_parts() -> None:
    loop = HabitLoop("阅读", "晚饭后", "阅读十分钟", "记录一条笔记")
    assert (loop.cue, loop.routine, loop.reward) == ("晚饭后", "阅读十分钟", "记录一条笔记")


def test_habit_loop_rejects_blank_parts() -> None:
    with pytest.raises(ValidationError, match="blank"):
        HabitLoop("阅读", "", "阅读十分钟", "记录")
