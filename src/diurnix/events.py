"""Typed, versioned personal events used throughout the runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from diurnix.errors import ValidationError
from diurnix.identifiers import validate_identifier


class EventKind(StrEnum):
    """Closed set of built-in personal event families."""

    INBOX_MESSAGE = "inbox_message"
    CALENDAR_ENTRY = "calendar_entry"
    TRANSACTION = "transaction"
    HABIT_CHECK_IN = "habit_check_in"
    TIMER_FIRE = "timer_fire"
    USER_UTTERANCE = "user_utterance"


@dataclass(frozen=True, slots=True)
class PersonalEvent:
    """Common identity and time fields for immutable personal events."""

    event_id: str
    occurred_at: datetime

    KIND: ClassVar[EventKind]
    SCHEMA_VERSION: ClassVar[int] = 1

    def __post_init__(self) -> None:
        validate_identifier(self.event_id, label="event_id")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValidationError("event time must be timezone-aware", path="$.occurred_at")

    @property
    def kind(self) -> EventKind:
        """Return the concrete wire kind."""
        return self.KIND


def event_sort_key(event: PersonalEvent) -> tuple[datetime, str]:
    """Order events by instant and then stable identifier."""
    return event.occurred_at, event.event_id


class InboxLabel(StrEnum):
    """Planted synthetic inbox intent labels."""

    ACTION_REQUIRED = "action_required"
    FYI = "fyi"
    NEWSLETTER = "newsletter"
    SPAM = "spam"
    PHISHING = "phishing"


@dataclass(frozen=True, slots=True)
class InboxMessage(PersonalEvent):
    """Synthetic inbox message with planted ground-truth label."""

    sender: str
    recipients: tuple[str, ...]
    subject: str
    body: str
    planted_label: InboxLabel
    priority: int = 0

    KIND: ClassVar[EventKind] = EventKind.INBOX_MESSAGE

    def __post_init__(self) -> None:
        PersonalEvent.__post_init__(self)
        if "@" not in self.sender:
            raise ValidationError("sender must resemble an email address", path="$.sender")
        if not self.recipients or any("@" not in item for item in self.recipients):
            raise ValidationError("recipients must contain email addresses", path="$.recipients")
        if not self.subject.strip():
            raise ValidationError("message subject must not be blank", path="$.subject")
        if not 0 <= self.priority <= 3:
            raise ValidationError("message priority must be from zero to three", path="$.priority")


@dataclass(frozen=True, slots=True)
class CalendarEntry(PersonalEvent):
    """Calendar interval with optional travel time planted by the factory."""

    title: str
    starts_at: datetime
    ends_at: datetime
    location: str = ""
    travel_minutes: int = 0
    planted_conflict: bool = False

    KIND: ClassVar[EventKind] = EventKind.CALENDAR_ENTRY

    def __post_init__(self) -> None:
        PersonalEvent.__post_init__(self)
        if not self.title.strip():
            raise ValidationError("calendar title must not be blank", path="$.title")
        for path, value in (("starts_at", self.starts_at), ("ends_at", self.ends_at)):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValidationError("calendar bounds must be timezone-aware", path=f"$.{path}")
        if self.ends_at.timestamp() <= self.starts_at.timestamp():
            raise ValidationError("calendar entry must have positive duration", path="$.ends_at")
        if self.travel_minutes < 0:
            raise ValidationError("travel minutes cannot be negative", path="$.travel_minutes")

    @property
    def duration_minutes(self) -> int:
        """Return elapsed duration rather than wall-clock label difference."""
        return int((self.ends_at.timestamp() - self.starts_at.timestamp()) // 60)
