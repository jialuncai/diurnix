"""Complete deterministic synthetic personal-data bundle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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


def generate_bundle(seed: int, start: datetime) -> SyntheticBundle:
    """Generate all four synthetic domains with documented planted truth."""
    from diurnix.persona_factory import create_persona
    from diurnix.synthetic import generate_inbox_week, inbox_ground_truth
    from diurnix.synthetic_calendar import (
        calendar_ground_truth,
        calendar_week_with_conflict,
        with_travel_constraints,
    )
    from diurnix.synthetic_habits import (
        generate_habit_stream,
        habit_ground_truth,
        plant_habit_lapse,
    )
    from diurnix.synthetic_ledger import generate_planted_ledger_month, ledger_ground_truth

    persona = create_persona(seed)
    inbox = generate_inbox_week(persona, seed, start)
    calendar = with_travel_constraints(
        calendar_week_with_conflict(persona, seed, start.date()), seed
    )
    ledger = generate_planted_ledger_month(persona, seed, start)
    habits = generate_habit_stream(persona, seed, start.date())
    habits = plant_habit_lapse(habits, persona.habit_goals[0].name, start.date(), days=3)
    truth = {
        "inbox": inbox_ground_truth(inbox),
        "calendar": calendar_ground_truth(calendar),
        "ledger": ledger_ground_truth(ledger),
        "habits": habit_ground_truth(habits),
    }
    return SyntheticBundle(seed, persona, inbox, calendar, ledger, habits, truth)
