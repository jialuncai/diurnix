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


class MemoryStore:
    def __init__(self, notes: tuple[MemoryNote, ...] = ()) -> None:
        self._notes: dict[str, MemoryNote] = {}
        for note in notes:
            self.add(note)

    def add(self, note: MemoryNote) -> None:
        if note.note_id in self._notes:
            raise ValidationError(f"duplicate memory note: {note.note_id}")
        self._notes[note.note_id] = note

    def get(self, note_id: str) -> MemoryNote:
        try:
            return self._notes[note_id]
        except KeyError as error:
            raise ValidationError(f"unknown memory note: {note_id}") from error

    def notes(self, scope: MemoryScope | None = None) -> tuple[MemoryNote, ...]:
        notes = tuple(self._notes.values())
        if scope is not None:
            notes = tuple(note for note in notes if note.scope is scope)
        return tuple(sorted(notes, key=lambda note: (note.created_at, note.note_id)))


_PRIVACY_LEVEL = {PrivacyTier.PUBLIC: 0, PrivacyTier.PERSONAL: 1, PrivacyTier.SENSITIVE: 2}


def can_read_memory(note: MemoryNote, reader_tier: PrivacyTier) -> bool:
    return _PRIVACY_LEVEL[reader_tier] >= _PRIVACY_LEVEL[note.privacy]


def visible_memories(store: MemoryStore, reader_tier: PrivacyTier) -> tuple[MemoryNote, ...]:
    return tuple(note for note in store.notes() if can_read_memory(note, reader_tier))
