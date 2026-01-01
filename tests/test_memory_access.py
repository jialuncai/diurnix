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


def test_memory_access_record_never_contains_note_content() -> None:
    note = make_memory_note(
        "n",
        MemoryScope.PERSISTENT,
        PrivacyTier.SENSITIVE,
        "card 4111 1111 1111 1111",
        (),
        datetime(2026, 1, 1, tzinfo=UTC),
    )
    _, log = MemoryAccessLog().check(note, PrivacyTier.PUBLIC)
    assert "4111" not in repr(log.records[0])


def test_access_log_preserves_prior_records() -> None:
    _, first = MemoryAccessLog().check(_note(PrivacyTier.PUBLIC), PrivacyTier.PUBLIC)
    _, second = first.check(_note(PrivacyTier.SENSITIVE), PrivacyTier.PUBLIC)
    assert tuple(record.sequence for record in second.records) == (0, 1)
    assert first.records == second.records[:1]
