"""Deterministic mechanics for offline personal-agent applications."""

from diurnix._version import __version__
from diurnix.artifacts import ArtifactEnvelope
from diurnix.budgets import Budget, Usage
from diurnix.clock import SyntheticClock
from diurnix.errors import DiurnixError, IntegrityError, ValidationError
from diurnix.events import (
    CalendarEntry,
    HabitCheckIn,
    InboxMessage,
    PersonalEvent,
    TimerFire,
    Transaction,
    UserUtterance,
)
from diurnix.factory import SyntheticBundle, generate_bundle
from diurnix.persona import Persona
from diurnix.randomness import SeededRandom

__all__ = [
    "ArtifactEnvelope",
    "Budget",
    "CalendarEntry",
    "DiurnixError",
    "HabitCheckIn",
    "InboxMessage",
    "IntegrityError",
    "Persona",
    "PersonalEvent",
    "SeededRandom",
    "SyntheticBundle",
    "SyntheticClock",
    "TimerFire",
    "Transaction",
    "Usage",
    "UserUtterance",
    "ValidationError",
    "__version__",
    "generate_bundle",
]
