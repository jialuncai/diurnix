"""Strict checksummed JSONL streams for personal events."""

from __future__ import annotations

from collections.abc import Iterable

from diurnix.artifacts import ArtifactEnvelope
from diurnix.event_codec import event_from_envelope, event_to_envelope
from diurnix.events import PersonalEvent


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
