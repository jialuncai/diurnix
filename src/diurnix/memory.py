"""Deterministic tiered memory with explicit privacy visibility."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from diurnix.errors import ValidationError


class MemoryScope(StrEnum):
    WORKING = "working"
    SESSION = "session"
    PERSISTENT = "persistent"


class PrivacyTier(StrEnum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


@dataclass(frozen=True, slots=True)
class MemoryNote:
    note_id: str
    scope: MemoryScope
    privacy: PrivacyTier
    content: str
    tags: tuple[str, ...]
    created_at: datetime


def make_memory_note(
    note_id: str,
    scope: MemoryScope,
    privacy: PrivacyTier,
    content: str,
    tags: tuple[str, ...],
    created_at: datetime,
) -> MemoryNote:
    if not note_id.strip():
        raise ValidationError("memory note id must not be blank")
    if not content.strip():
        raise ValidationError("memory note content must not be blank")
    if created_at.tzinfo is None or created_at.utcoffset() is None:
        raise ValidationError("memory note time must be timezone-aware")
    normalized_tags = tuple(sorted({tag.strip().casefold() for tag in tags if tag.strip()}))
    return MemoryNote(note_id, scope, privacy, content, normalized_tags, created_at)
