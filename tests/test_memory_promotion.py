from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import MemoryScope, PrivacyTier, make_memory_note, promote_memory


def _note(scope: MemoryScope = MemoryScope.WORKING):
    return make_memory_note(
        "n",
        scope,
        PrivacyTier.PERSONAL,
        "value",
        ("tag",),
        datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_memory_promotion_preserves_note_identity() -> None:
    promoted = promote_memory(_note(), MemoryScope.PERSISTENT)
    assert promoted.scope is MemoryScope.PERSISTENT
    assert promoted.note_id == "n" and promoted.content == "value"


def test_memory_promotion_rejects_demotion() -> None:
    with pytest.raises(ValidationError, match="shorter-lived"):
        promote_memory(_note(MemoryScope.PERSISTENT), MemoryScope.SESSION)


def test_promotion_never_lowers_privacy_tier() -> None:
    for privacy in PrivacyTier:
        note = make_memory_note(
            privacy.value,
            MemoryScope.WORKING,
            privacy,
            "value",
            (),
            datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert promote_memory(note, MemoryScope.PERSISTENT).privacy is privacy


def test_same_scope_promotion_is_value_preserving() -> None:
    note = _note(MemoryScope.SESSION)
    assert promote_memory(note, MemoryScope.SESSION) == note
