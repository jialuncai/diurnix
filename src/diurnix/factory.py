"""Complete deterministic synthetic personal-data bundle."""

from __future__ import annotations

from dataclasses import dataclass

from diurnix.events import CalendarEntry, HabitCheckIn, InboxMessage, Transaction
from diurnix.persona import Persona


@dataclass(frozen=True, slots=True)
class SyntheticBundle:
    """Persona, four event streams, and their planted truth manifests."""

    seed: int
    persona: Persona
    inbox: tuple[InboxMessage, ...]
    calendar: tuple[CalendarEntry, ...]
    ledger: tuple[Transaction, ...]
    habits: tuple[HabitCheckIn, ...]
    ground_truth: dict[str, object]

    @property
    def event_count(self) -> int:
        """Count events across all four daily-life domains."""
        return len(self.inbox) + len(self.calendar) + len(self.ledger) + len(self.habits)
