"""Strict checksummed JSONL streams for personal events."""

from __future__ import annotations

from collections.abc import Iterable

from diurnix.event_codec import event_to_envelope
from diurnix.events import PersonalEvent


def events_to_jsonl(events: Iterable[PersonalEvent]) -> str:
    """Encode one canonical integrity envelope per line with a final newline."""
    lines = [event_to_envelope(event).to_json() for event in events]
    return "" if not lines else "\n".join(lines) + "\n"
