from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.tasks_app import TaskStatus, make_task, task_from_dict, task_to_dict

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def _task():
    return make_task(
        "task-1",
        "完成周报",
        NOW,
        deadline=NOW + timedelta(days=1),
        importance=4,
        effort_minutes=45,
        status=TaskStatus.NEXT,
        context="computer",
    )


def test_task_mapping_roundtrips_every_field() -> None:
    assert task_from_dict(task_to_dict(_task())) == _task()


def test_task_mapping_has_golden_keys() -> None:
    assert list(task_to_dict(_task())) == [
        "schema_version",
        "task_id",
        "title",
        "captured_at",
        "deadline",
        "importance",
        "effort_minutes",
        "status",
        "context",
    ]


def test_task_codec_rejects_extensions() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = task_to_dict(_task())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        task_from_dict(encoded)


def test_task_codec_rejects_unknown_status() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = task_to_dict(_task())
    encoded["status"] = "lost"
    with pytest.raises(ValidationError, match="invalid task"):
        task_from_dict(encoded)


def test_task_codec_rejects_coerced_numeric_fields() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = task_to_dict(_task())
    with pytest.raises(ValidationError, match="integers"):
        task_from_dict({**encoded, "importance": "4"})
    with pytest.raises(ValidationError, match="integers"):
        task_from_dict({**encoded, "effort_minutes": True})
