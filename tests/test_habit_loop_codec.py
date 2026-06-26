from __future__ import annotations

from diurnix.habits_app import HabitLoop, habit_loop_from_dict, habit_loop_to_dict


def test_habit_loop_mapping_roundtrips() -> None:
    loop = HabitLoop("阅读", "晚饭后", "阅读十分钟", "记录笔记")
    assert habit_loop_from_dict(habit_loop_to_dict(loop)) == loop


def test_habit_loop_mapping_has_golden_keys() -> None:
    encoded = habit_loop_to_dict(HabitLoop("阅读", "晚饭后", "十分钟", "记录"))
    assert list(encoded) == ["schema_version", "habit", "cue", "routine", "reward"]


def test_habit_loop_codec_rejects_extensions() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = habit_loop_to_dict(HabitLoop("阅读", "晚饭后", "十分钟", "记录"))
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        habit_loop_from_dict(encoded)


def test_habit_loop_codec_reuses_blank_validation() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = habit_loop_to_dict(HabitLoop("阅读", "晚饭后", "十分钟", "记录"))
    encoded["reward"] = " "
    with pytest.raises(ValidationError, match="blank"):
        habit_loop_from_dict(encoded)
