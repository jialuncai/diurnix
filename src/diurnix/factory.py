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


def bundle_manifest(bundle: SyntheticBundle) -> dict[str, object]:
    """Checksum each event stream and the complete planted truth mapping."""
    from diurnix.event_stream import event_manifest
    from diurnix.integrity import content_checksum
    from diurnix.persona_codec import persona_to_dict

    return {
        "factory": "diurnix.synthetic-bundle",
        "factory_version": 1,
        "seed": bundle.seed,
        "persona_checksum": content_checksum(persona_to_dict(bundle.persona)),
        "streams": {
            "inbox": event_manifest(bundle.inbox),
            "calendar": event_manifest(bundle.calendar),
            "ledger": event_manifest(bundle.ledger),
            "habits": event_manifest(bundle.habits),
        },
        "ground_truth_checksum": content_checksum(bundle.ground_truth),
        "ground_truth": bundle.ground_truth,
    }


def audit_bundle(bundle: SyntheticBundle) -> tuple[str, ...]:
    """Return deterministic completeness errors without mutating a bundle."""
    errors = []
    for name in ("inbox", "calendar", "ledger", "habits"):
        if not getattr(bundle, name):
            errors.append(f"{name} stream is empty")
        if name not in bundle.ground_truth:
            errors.append(f"{name} truth is missing")
    identities = [
        event.event_id
        for stream in (bundle.inbox, bundle.calendar, bundle.ledger, bundle.habits)
        for event in stream
    ]
    if len(set(identities)) != len(identities):
        errors.append("event identities are not globally unique")
    return tuple(errors)
