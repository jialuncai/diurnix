from __future__ import annotations

from datetime import UTC, datetime

from diurnix.codec import canonical_dumps
from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    export_visible_memory,
    make_memory_note,
)


def _note(note_id: str, tier: PrivacyTier, content: str):
    return make_memory_note(
        note_id, MemoryScope.PERSISTENT, tier, content, (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_public_export_excludes_planted_sensitive_pii() -> None:
    store = MemoryStore(
        (
            _note("public", PrivacyTier.PUBLIC, "weather preference"),
            _note("card", PrivacyTier.SENSITIVE, "4111 1111 1111 1111"),
        )
    )
    encoded = canonical_dumps(export_visible_memory(store, PrivacyTier.PUBLIC))
    assert "weather preference" in encoded
    assert "4111" not in encoded and "card" not in encoded


def test_sensitive_export_includes_every_tier() -> None:
    store = MemoryStore(tuple(_note(tier.value, tier, tier.value) for tier in PrivacyTier))
    assert export_visible_memory(store, PrivacyTier.SENSITIVE)["note_count"] == 3


def test_exported_note_tiers_never_exceed_reader_tier() -> None:
    levels = {PrivacyTier.PUBLIC: 0, PrivacyTier.PERSONAL: 1, PrivacyTier.SENSITIVE: 2}
    store = MemoryStore(
        tuple(
            _note(f"{index}-{tier.value}", tier, f"planted-{index}-{tier.value}")
            for index in range(5)
            for tier in PrivacyTier
        )
    )
    for reader in PrivacyTier:
        exported = export_visible_memory(store, reader)
        assert all(
            levels[PrivacyTier(note["privacy"])] <= levels[reader] for note in exported["notes"]
        )


def test_export_count_matches_serialized_rows() -> None:
    store = MemoryStore(tuple(_note(tier.value, tier, tier.value) for tier in PrivacyTier))
    for reader in PrivacyTier:
        exported = export_visible_memory(store, reader)
        assert exported["note_count"] == len(exported["notes"])
