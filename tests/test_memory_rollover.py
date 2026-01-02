from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    make_memory_note,
    roll_working_to_session,
)


def _note(note_id: str, scope: MemoryScope):
    return make_memory_note(
        note_id, scope, PrivacyTier.PERSONAL, note_id, (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_rollover_promotes_working_and_keeps_other_scopes() -> None:
    source = MemoryStore((_note("w", MemoryScope.WORKING), _note("p", MemoryScope.PERSISTENT)))
    rolled = roll_working_to_session(source)
    assert rolled.get("w").scope is MemoryScope.SESSION
    assert rolled.get("p").scope is MemoryScope.PERSISTENT


def test_rollover_does_not_mutate_source() -> None:
    source = MemoryStore((_note("w", MemoryScope.WORKING),))
    roll_working_to_session(source)
    assert source.get("w").scope is MemoryScope.WORKING
