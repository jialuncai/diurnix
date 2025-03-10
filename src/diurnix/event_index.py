"""Immutable identity index over a personal-event history."""

from __future__ import annotations

from collections.abc import Iterable

from diurnix.errors import ValidationError
from diurnix.event_stream import deduplicate_events
from diurnix.events import EventKind, PersonalEvent, event_sort_key


class EventIndex:
    """Validated read-only lookup structure with stable chronology."""

    def __init__(self, events: Iterable[PersonalEvent]) -> None:
        ordered = tuple(sorted(deduplicate_events(events), key=event_sort_key))
        self._events = ordered
        self._by_id = {event.event_id: event for event in ordered}

    def __len__(self) -> int:
        return len(self._events)

    def all(self) -> tuple[PersonalEvent, ...]:
        """Return every indexed event in stable chronology."""
        return self._events

    def get(self, event_id: str) -> PersonalEvent | None:
        """Find an event or return ``None`` without synthesizing data."""
        return self._by_id.get(event_id)

    def require(self, event_id: str) -> PersonalEvent:
        """Find an event or raise a precise validation error."""
        event = self.get(event_id)
        if event is None:
            raise ValidationError(f"event not found: {event_id}", path="$.event_id")
        return event

    def count_by_kind(self) -> dict[EventKind, int]:
        """Count present event families, omitting zero-count kinds."""
        counts: dict[EventKind, int] = {}
        for event in self._events:
            counts[event.kind] = counts.get(event.kind, 0) + 1
        return counts
