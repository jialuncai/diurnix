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

    def remove(self, note_id: str) -> MemoryNote:
        try:
            return self._notes.pop(note_id)
        except KeyError as error:
            raise ValidationError(f"unknown memory note: {note_id}") from error

    def clear_scope(self, scope: MemoryScope) -> tuple[MemoryNote, ...]:
        removed = self.notes(scope)
        for note in removed:
            del self._notes[note.note_id]
        return removed


_PRIVACY_LEVEL = {PrivacyTier.PUBLIC: 0, PrivacyTier.PERSONAL: 1, PrivacyTier.SENSITIVE: 2}


def can_read_memory(note: MemoryNote, reader_tier: PrivacyTier) -> bool:
    return _PRIVACY_LEVEL[reader_tier] >= _PRIVACY_LEVEL[note.privacy]


def visible_memories(store: MemoryStore, reader_tier: PrivacyTier) -> tuple[MemoryNote, ...]:
    return tuple(note for note in store.notes() if can_read_memory(note, reader_tier))


def query_memory_tags(
    store: MemoryStore, tags: tuple[str, ...], *, match_all: bool = True
) -> tuple[MemoryNote, ...]:
    wanted = {tag.strip().casefold() for tag in tags if tag.strip()}
    if not wanted:
        raise ValidationError("memory tag query cannot be empty")
    matches = []
    for note in store.notes():
        present = set(note.tags)
        if (wanted <= present) if match_all else bool(wanted & present):
            matches.append(note)
    return tuple(matches)


def episodic_buckets(
    notes: tuple[MemoryNote, ...], timezone_name: str
) -> dict[str, tuple[MemoryNote, ...]]:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as error:
        raise ValidationError(f"unknown episodic timezone: {timezone_name}") from error
    buckets: dict[str, list[MemoryNote]] = {}
    for note in sorted(notes, key=lambda item: (item.created_at, item.note_id)):
        day = note.created_at.astimezone(zone).date().isoformat()
        buckets.setdefault(day, []).append(note)
    return {day: tuple(items) for day, items in sorted(buckets.items())}


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    working_days: float = 1.0
    session_days: float = 7.0
    persistent_days: float = 365.0
    minimum_score: float = 0.1

    def __post_init__(self) -> None:
        if min(self.working_days, self.session_days, self.persistent_days) <= 0:
            raise ValidationError("retention windows must be positive")
        if not 0 <= self.minimum_score <= 1:
            raise ValidationError("minimum retention score must be between zero and one")

    def days_for(self, scope: MemoryScope) -> float:
        return {
            MemoryScope.WORKING: self.working_days,
            MemoryScope.SESSION: self.session_days,
            MemoryScope.PERSISTENT: self.persistent_days,
        }[scope]


def retention_score(note: MemoryNote, now: datetime, policy: RetentionPolicy) -> float:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValidationError("retention time must be timezone-aware")
    age_days = max(0.0, (now - note.created_at).total_seconds() / 86400)
    score = max(0.0, 1.0 - age_days / policy.days_for(note.scope))
    return round(score, 6)


def partition_retained_memory(
    notes: tuple[MemoryNote, ...], now: datetime, policy: RetentionPolicy
) -> tuple[tuple[MemoryNote, ...], tuple[MemoryNote, ...]]:
    retained = []
    forgotten = []
    for note in sorted(notes, key=lambda item: (item.created_at, item.note_id)):
        target = (
            retained if retention_score(note, now, policy) >= policy.minimum_score else forgotten
        )
        target.append(note)
    return tuple(retained), tuple(forgotten)


def memory_snapshot(store: MemoryStore) -> dict[str, object]:
    from diurnix.integrity import content_checksum

    notes = [memory_note_to_dict(note) for note in store.notes()]
    return {"schema_version": 1, "checksum": content_checksum(notes), "notes": notes}


def restore_memory_snapshot(value: dict[str, object]) -> MemoryStore:
    from diurnix.integrity import verify_content

    if set(value) != {"schema_version", "checksum", "notes"} or value.get("schema_version") != 1:
        raise ValidationError("memory snapshot does not match schema")
    notes = value["notes"]
    if not isinstance(notes, list) or not all(isinstance(note, dict) for note in notes):
        raise ValidationError("memory snapshot notes must be objects")
    verify_content(notes, str(value["checksum"]))
    return MemoryStore(tuple(memory_note_from_dict(note) for note in notes))


def memory_manifest(store: MemoryStore, seed: int) -> dict[str, object]:
    from diurnix.integrity import content_checksum

    counts = {scope.value: len(store.notes(scope)) for scope in MemoryScope}
    snapshot = memory_snapshot(store)
    return {
        "kind": "memory.snapshot",
        "schema_version": 1,
        "seed": seed,
        "synthetic": True,
        "scope_counts": counts,
        "snapshot_checksum": content_checksum(snapshot),
    }


def promote_memory(note: MemoryNote, target: MemoryScope) -> MemoryNote:
    from dataclasses import replace

    levels = {MemoryScope.WORKING: 0, MemoryScope.SESSION: 1, MemoryScope.PERSISTENT: 2}
    if levels[target] < levels[note.scope]:
        raise ValidationError("memory promotion cannot move to a shorter-lived scope")
    return replace(note, scope=target)


def enforce_working_capacity(
    store: MemoryStore, capacity: int
) -> tuple[MemoryStore, tuple[MemoryNote, ...]]:
    if capacity < 0:
        raise ValidationError("working memory capacity cannot be negative")
    working = store.notes(MemoryScope.WORKING)
    evicted_count = max(0, len(working) - capacity)
    evicted = working[:evicted_count]
    evicted_ids = {note.note_id for note in evicted}
    retained = tuple(note for note in store.notes() if note.note_id not in evicted_ids)
    return MemoryStore(retained), evicted
