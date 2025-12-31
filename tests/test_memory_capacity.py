from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    enforce_working_capacity,
    make_memory_note,
)


def _note(note_id: str, hour: int, scope: MemoryScope = MemoryScope.WORKING):
    return make_memory_note(
        note_id, scope, PrivacyTier.PUBLIC, note_id, (), datetime(2026, 1, 1, hour, tzinfo=UTC)
    )


def test_working_capacity_evicts_oldest_notes() -> None:
    store = MemoryStore(tuple(_note(f"n-{hour}", hour) for hour in range(4)))
    bounded, evicted = enforce_working_capacity(store, 2)
    assert tuple(note.note_id for note in evicted) == ("n-0", "n-1")
    assert tuple(note.note_id for note in bounded.notes()) == ("n-2", "n-3")


def test_working_capacity_rejects_negative_limit() -> None:
    with pytest.raises(ValidationError, match="negative"):
        enforce_working_capacity(MemoryStore(), -1)
