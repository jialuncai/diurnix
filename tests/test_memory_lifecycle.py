from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import MemoryScope, MemoryStore, PrivacyTier, make_memory_note


def _note(note_id: str, scope: MemoryScope):
    return make_memory_note(
        note_id, scope, PrivacyTier.PUBLIC, note_id, (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_memory_store_removes_one_note() -> None:
    store = MemoryStore((_note("a", MemoryScope.WORKING), _note("b", MemoryScope.SESSION)))
    assert store.remove("a").note_id == "a"
    assert tuple(note.note_id for note in store.notes()) == ("b",)


def test_memory_store_clears_only_requested_scope() -> None:
    store = MemoryStore((_note("w", MemoryScope.WORKING), _note("p", MemoryScope.PERSISTENT)))
    assert store.clear_scope(MemoryScope.WORKING) == (_note("w", MemoryScope.WORKING),)
    assert store.notes() == (_note("p", MemoryScope.PERSISTENT),)


def test_clearing_empty_scope_is_idempotent() -> None:
    store = MemoryStore((_note("p", MemoryScope.PERSISTENT),))
    assert store.clear_scope(MemoryScope.WORKING) == ()
    assert store.clear_scope(MemoryScope.WORKING) == ()
    assert len(store.notes()) == 1


def test_removed_note_cannot_be_read_again() -> None:
    import pytest

    from diurnix.errors import ValidationError

    store = MemoryStore((_note("w", MemoryScope.WORKING),))
    store.remove("w")
    with pytest.raises(ValidationError, match="unknown"):
        store.get("w")
