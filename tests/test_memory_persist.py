from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    make_memory_note,
    persist_tagged_memory,
)


def _note(note_id: str, tags: tuple[str, ...]):
    return make_memory_note(
        note_id,
        MemoryScope.SESSION,
        PrivacyTier.PERSONAL,
        note_id,
        tags,
        datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_persist_tagged_memory_promotes_matching_notes() -> None:
    store = MemoryStore((_note("keep", ("preference",)), _note("drop", ("transient",))))
    result = persist_tagged_memory(store, ("preference",))
    assert result.get("keep").scope is MemoryScope.PERSISTENT
    assert result.get("drop").scope is MemoryScope.SESSION
