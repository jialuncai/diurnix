from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    make_memory_note,
    query_memory_tags,
)


def _note(note_id: str, tags: tuple[str, ...]):
    return make_memory_note(
        note_id,
        MemoryScope.PERSISTENT,
        PrivacyTier.PUBLIC,
        note_id,
        tags,
        datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_memory_tag_query_supports_all_and_any_modes() -> None:
    store = MemoryStore((_note("a", ("work", "urgent")), _note("b", ("home", "urgent"))))
    assert tuple(note.note_id for note in query_memory_tags(store, ("work", "urgent"))) == ("a",)
    assert tuple(
        note.note_id for note in query_memory_tags(store, ("work", "home"), match_all=False)
    ) == ("a", "b")


def test_memory_tag_query_rejects_empty_terms() -> None:
    with pytest.raises(ValidationError, match="empty"):
        query_memory_tags(MemoryStore(), (" ",))
