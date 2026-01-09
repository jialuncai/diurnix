from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import MemoryScope, MemoryStore, PrivacyTier, make_memory_note, memory_metrics


def test_memory_metrics_keep_zero_count_categories() -> None:
    note = make_memory_note(
        "n",
        MemoryScope.WORKING,
        PrivacyTier.PUBLIC,
        "value",
        ("a", "b"),
        datetime(2026, 1, 1, tzinfo=UTC),
    )
    metrics = memory_metrics(MemoryStore((note,)))
    assert metrics["scope_counts"] == {"working": 1, "session": 0, "persistent": 0}
    assert metrics["privacy_counts"] == {"public": 1, "personal": 0, "sensitive": 0}
    assert metrics["tag_count"] == 2


def test_empty_memory_metrics_are_explicit() -> None:
    metrics = memory_metrics(MemoryStore())
    assert metrics["note_count"] == 0 and metrics["tag_count"] == 0
