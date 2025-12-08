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


def test_memory_note_codec_rejects_extensions() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = memory_note_to_dict(_note())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        memory_note_from_dict(encoded)


def test_memory_note_codec_rejects_non_string_tags() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = memory_note_to_dict(_note())
    encoded["tags"] = [1]
    with pytest.raises(ValidationError, match="tags"):
        memory_note_from_dict(encoded)
