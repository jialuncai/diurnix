from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.memory import (
    MemoryScope,
    PrivacyTier,
    RetentionPolicy,
    make_memory_note,
    partition_retained_memory,
)


def _note(note_id: str, age: int):
    now = datetime(2026, 1, 10, tzinfo=UTC)
    return make_memory_note(
        note_id, MemoryScope.WORKING, PrivacyTier.PUBLIC, note_id, (), now - timedelta(days=age)
    )


def test_forgetting_partitions_at_configured_threshold() -> None:
    now = datetime(2026, 1, 10, tzinfo=UTC)
    kept, forgotten = partition_retained_memory(
        (_note("old", 10), _note("new", 0)), now, RetentionPolicy(working_days=2)
    )
    assert tuple(note.note_id for note in kept) == ("new",)
    assert tuple(note.note_id for note in forgotten) == ("old",)
