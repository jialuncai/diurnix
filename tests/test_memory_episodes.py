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


def test_fall_back_repeated_hour_stays_in_one_episode() -> None:
    first = _note("first", datetime.fromisoformat("2026-11-01T05:30:00+00:00"))
    second = _note("second", datetime.fromisoformat("2026-11-01T06:30:00+00:00"))
    buckets = episodic_buckets((second, first), "America/New_York")
    assert tuple(buckets) == ("2026-11-01",)
    assert tuple(note.note_id for note in buckets["2026-11-01"]) == ("first", "second")


def test_spring_forward_events_keep_instant_order() -> None:
    before = _note("before", datetime.fromisoformat("2026-03-08T06:59:00+00:00"))
    after = _note("after", datetime.fromisoformat("2026-03-08T07:01:00+00:00"))
    bucket = episodic_buckets((after, before), "America/New_York")["2026-03-08"]
    assert tuple(note.note_id for note in bucket) == ("before", "after")
