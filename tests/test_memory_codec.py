from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryScope,
    PrivacyTier,
    make_memory_note,
    memory_note_from_dict,
    memory_note_to_dict,
)


def _note():
    return make_memory_note(
        "note-1",
        MemoryScope.PERSISTENT,
        PrivacyTier.SENSITIVE,
        "Synthetic account reminder",
        ("finance",),
        datetime(2026, 10, 30, 1, tzinfo=UTC),
    )


def test_memory_note_mapping_roundtrips() -> None:
    assert memory_note_from_dict(memory_note_to_dict(_note())) == _note()


def test_memory_note_mapping_has_golden_key_order() -> None:
    assert list(memory_note_to_dict(_note())) == [
        "schema_version",
        "note_id",
        "scope",
        "privacy",
        "content",
        "tags",
        "created_at",
    ]
