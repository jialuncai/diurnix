"""Strict checksummed JSONL streams for personal events."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from diurnix.artifacts import ArtifactEnvelope
from diurnix.errors import ValidationError
from diurnix.event_codec import event_from_envelope, event_to_envelope
from diurnix.events import EventKind, PersonalEvent


def events_to_jsonl(events: Iterable[PersonalEvent]) -> str:
    """Encode one canonical integrity envelope per line with a final newline."""
    lines = [event_to_envelope(event).to_json() for event in events]
    return "" if not lines else "\n".join(lines) + "\n"


def events_from_jsonl(text: str) -> tuple[PersonalEvent, ...]:
    """Decode and integrity-check every nonblank JSONL record."""
    if not text:
        return ()
    return tuple(
        event_from_envelope(ArtifactEnvelope.from_json(line)) for line in text.splitlines()
    )


def append_event(path: Path, event: PersonalEvent) -> None:
    """Append exactly one encoded event, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(events_to_jsonl((event,)))


def read_event_file(path: Path) -> tuple[PersonalEvent, ...]:
    """Read a complete UTF-8 event log, treating a missing file as empty."""
    if not path.exists():
        return ()
    return events_from_jsonl(path.read_text(encoding="utf-8"))


def events_of_kind(
    events: Iterable[PersonalEvent], kinds: EventKind | Iterable[EventKind]
) -> tuple[PersonalEvent, ...]:
    """Select events whose concrete family is in the requested set."""
    accepted = {kinds} if isinstance(kinds, EventKind) else set(kinds)
    return tuple(event for event in events if event.kind in accepted)


def events_between(
    events: Iterable[PersonalEvent], start: datetime, end: datetime
) -> tuple[PersonalEvent, ...]:
    """Select events in the half-open absolute-time interval ``[start, end)``."""
    if any(value.tzinfo is None or value.utcoffset() is None for value in (start, end)):
        raise ValidationError("event query bounds must be timezone-aware")
    if end.timestamp() < start.timestamp():
        raise ValidationError("event query end precedes start")
    start_ts, end_ts = start.timestamp(), end.timestamp()
    return tuple(event for event in events if start_ts <= event.occurred_at.timestamp() < end_ts)


def deduplicate_events(events: Iterable[PersonalEvent]) -> tuple[PersonalEvent, ...]:
    """Keep first identical IDs and reject IDs reused for different content."""
    seen: dict[str, PersonalEvent] = {}
    result: list[PersonalEvent] = []
    for event in events:
        previous = seen.get(event.event_id)
        if previous is None:
            seen[event.event_id] = event
            result.append(event)
        elif previous != event:
            raise ValidationError(f"conflicting event id: {event.event_id}", path="$.event_id")
    return tuple(result)
