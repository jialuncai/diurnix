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


def test_persistence_preserves_content_tags_and_privacy() -> None:
    note = _note("keep", ("preference", "work"))
    promoted = persist_tagged_memory(MemoryStore((note,)), ("work",)).get("keep")
    assert promoted.content == note.content
    assert promoted.tags == note.tags
    assert promoted.privacy is note.privacy


def test_persistence_matches_any_requested_tag() -> None:
    store = MemoryStore((_note("a", ("alpha",)), _note("b", ("beta",))))
    result = persist_tagged_memory(store, ("alpha", "missing"))
    assert result.get("a").scope is MemoryScope.PERSISTENT
    assert result.get("b").scope is MemoryScope.SESSION
