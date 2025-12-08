from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from diurnix.memory import MemoryScope, PrivacyTier, make_memory_note


def test_memory_note_normalizes_tags_deterministically() -> None:
    note = make_memory_note(
        "note-1",
        MemoryScope.SESSION,
        PrivacyTier.PERSONAL,
        "Synthetic preference",
        (" Work ", "work", "URGENT", ""),
        datetime(2026, 10, 30, 9, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    assert note.tags == ("urgent", "work")


def test_memory_scope_and_privacy_values_are_stable() -> None:
    assert tuple(MemoryScope) == ("working", "session", "persistent")
    assert tuple(PrivacyTier) == ("public", "personal", "sensitive")


def test_memory_note_rejects_blank_identity_and_content() -> None:
    import pytest

    from diurnix.errors import ValidationError

    aware = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    with pytest.raises(ValidationError, match="id"):
        make_memory_note(" ", MemoryScope.WORKING, PrivacyTier.PUBLIC, "value", (), aware)
    with pytest.raises(ValidationError, match="content"):
        make_memory_note("n", MemoryScope.WORKING, PrivacyTier.PUBLIC, " ", (), aware)


def test_memory_note_rejects_naive_time() -> None:
    import pytest

    from diurnix.errors import ValidationError

    with pytest.raises(ValidationError, match="timezone-aware"):
        make_memory_note(
            "n", MemoryScope.WORKING, PrivacyTier.PUBLIC, "value", (), datetime(2026, 1, 1)
        )
