"""Strict checksummed JSONL streams for personal events."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from diurnix.artifacts import ArtifactEnvelope
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
