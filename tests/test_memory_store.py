from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import MemoryScope, MemoryStore, PrivacyTier, make_memory_note


def _note(note_id: str, scope: MemoryScope):
    return make_memory_note(
        note_id, scope, PrivacyTier.PUBLIC, note_id, (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_memory_store_filters_scopes_without_reordering() -> None:
    store = MemoryStore((_note("p", MemoryScope.PERSISTENT), _note("w", MemoryScope.WORKING)))
    assert store.get("p").scope is MemoryScope.PERSISTENT
    assert store.notes(MemoryScope.WORKING) == (_note("w", MemoryScope.WORKING),)


def test_memory_store_returns_deterministic_id_order_for_ties() -> None:
    store = MemoryStore((_note("z", MemoryScope.SESSION), _note("a", MemoryScope.SESSION)))
    assert tuple(note.note_id for note in store.notes()) == ("a", "z")
