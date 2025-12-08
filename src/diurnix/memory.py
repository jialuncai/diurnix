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


def memory_note_to_dict(note: MemoryNote) -> dict[str, object]:
    return {
        "schema_version": 1,
        "note_id": note.note_id,
        "scope": note.scope.value,
        "privacy": note.privacy.value,
        "content": note.content,
        "tags": list(note.tags),
        "created_at": note.created_at.isoformat(),
    }


def memory_note_from_dict(value: dict[str, object]) -> MemoryNote:
    expected = {"schema_version", "note_id", "scope", "privacy", "content", "tags", "created_at"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("memory note does not match schema")
    tags = value["tags"]
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValidationError("memory note tags must be strings")
    try:
        created_at = datetime.fromisoformat(str(value["created_at"]))
        return make_memory_note(
            str(value["note_id"]),
            MemoryScope(str(value["scope"])),
            PrivacyTier(str(value["privacy"])),
            str(value["content"]),
            tuple(tags),
            created_at,
        )
    except ValueError as error:
        raise ValidationError(f"invalid memory note value: {error}") from error
