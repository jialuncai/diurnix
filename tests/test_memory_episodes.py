from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import MemoryScope, PrivacyTier, episodic_buckets, make_memory_note


def _note(note_id: str, created_at: datetime):
    return make_memory_note(
        note_id, MemoryScope.SESSION, PrivacyTier.PUBLIC, note_id, (), created_at
    )


def test_episodic_index_uses_reader_local_day() -> None:
    notes = (
        _note("late", datetime(2026, 10, 29, 16, 30, tzinfo=UTC)),
        _note("early", datetime(2026, 10, 30, 2, tzinfo=UTC)),
    )
    assert tuple(episodic_buckets(notes, "Asia/Shanghai")) == ("2026-10-30",)


def test_episodic_index_rejects_unknown_timezone() -> None:
    with pytest.raises(ValidationError, match="unknown"):
        episodic_buckets((), "Mars/Olympus")
