from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    can_read_memory,
    make_memory_note,
    visible_memories,
)


def _note(note_id: str, tier: PrivacyTier):
    return make_memory_note(
        note_id, MemoryScope.SESSION, tier, note_id, (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_lower_tier_reader_never_sees_higher_tier_content() -> None:
    store = MemoryStore(tuple(_note(tier.value, tier) for tier in PrivacyTier))
    assert tuple(note.note_id for note in visible_memories(store, PrivacyTier.PUBLIC)) == (
        "public",
    )
    assert tuple(note.note_id for note in visible_memories(store, PrivacyTier.PERSONAL)) == (
        "personal",
        "public",
    )


def test_sensitive_reader_can_read_all_tiers() -> None:
    assert all(
        can_read_memory(_note(tier.value, tier), PrivacyTier.SENSITIVE) for tier in PrivacyTier
    )
