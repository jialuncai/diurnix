from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryAccessLog,
    MemoryScope,
    PrivacyTier,
    make_memory_note,
)


def _note(tier: PrivacyTier):
    return make_memory_note(
        "n", MemoryScope.PERSISTENT, tier, "secret", (), datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_memory_access_log_is_immutable_and_contiguous() -> None:
    original = MemoryAccessLog()
    allowed, updated = original.check(_note(PrivacyTier.PUBLIC), PrivacyTier.PUBLIC)
    assert allowed is True and original.records == ()
    assert updated.records[0].sequence == 0


def test_memory_access_log_records_denial_reason() -> None:
    allowed, log = MemoryAccessLog().check(_note(PrivacyTier.SENSITIVE), PrivacyTier.PERSONAL)
    assert allowed is False
    assert log.records[0].reason == "privacy tier blocks read"
