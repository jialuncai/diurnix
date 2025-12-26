from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import IntegrityError
from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    make_memory_note,
    memory_snapshot,
    restore_memory_snapshot,
)


def _store():
    note = make_memory_note(
        "n",
        MemoryScope.PERSISTENT,
        PrivacyTier.PERSONAL,
        "value",
        ("tag",),
        datetime(2026, 1, 1, tzinfo=UTC),
    )
    return MemoryStore((note,))


def test_memory_snapshot_roundtrips_all_tiers() -> None:
    store = _store()
    assert restore_memory_snapshot(memory_snapshot(store)).notes() == store.notes()


def test_memory_snapshot_detects_tampering() -> None:
    snapshot = memory_snapshot(_store())
    snapshot["notes"][0]["content"] = "changed"
    with pytest.raises(IntegrityError, match="checksum"):
        restore_memory_snapshot(snapshot)
