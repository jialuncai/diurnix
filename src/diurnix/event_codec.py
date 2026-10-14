"""Canonical mapping codec for all built-in personal events."""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Any

from diurnix.artifacts import ArtifactEnvelope
from diurnix.errors import ValidationError
from diurnix.events import (
    AnomalyLabel,
    CalendarEntry,
    EventKind,
    HabitCheckIn,
    HabitStatus,
    InboxLabel,
    InboxMessage,
    PersonalEvent,
    TimerFire,
    Transaction,
    UserUtterance,
)


def event_to_dict(event: PersonalEvent) -> dict[str, Any]:
    """Encode dataclass fields plus explicit kind and schema metadata."""
    payload: dict[str, Any] = {}
    for field in fields(event):
        value = getattr(event, field.name)
        if isinstance(value, datetime):
            payload[field.name] = value.isoformat()
        elif isinstance(value, Enum):
            payload[field.name] = value.value
        elif isinstance(value, tuple):
            payload[field.name] = list(value)
        else:
            payload[field.name] = value
    return {
        "kind": event.kind.value,
        "schema_version": event.SCHEMA_VERSION,
        "payload": payload,
    }


def event_from_dict(value: dict[str, Any]) -> PersonalEvent:
    """Decode a strict version-one built-in event mapping."""
    if set(value) != {"kind", "schema_version", "payload"}:
        raise ValidationError("event fields do not match schema")
    if value["schema_version"] != 1:
        raise ValidationError("unsupported event schema version", path="$.schema_version")
    if not isinstance(value["payload"], dict):
        raise ValidationError("event payload must be an object", path="$.payload")
    payload = dict(value["payload"])
    try:
        kind = EventKind(value["kind"])
        payload["occurred_at"] = datetime.fromisoformat(payload["occurred_at"])
        if kind is EventKind.INBOX_MESSAGE:
            payload["recipients"] = tuple(payload["recipients"])
            payload["planted_label"] = InboxLabel(payload["planted_label"])
            return InboxMessage(**payload)
        if kind is EventKind.CALENDAR_ENTRY:
            payload["starts_at"] = datetime.fromisoformat(payload["starts_at"])
            payload["ends_at"] = datetime.fromisoformat(payload["ends_at"])
            return CalendarEntry(**payload)
        if kind is EventKind.TRANSACTION:
            payload["planted_anomaly"] = AnomalyLabel(payload["planted_anomaly"])
            return Transaction(**payload)
        if kind is EventKind.HABIT_CHECK_IN:
            payload["status"] = HabitStatus(payload["status"])
            return HabitCheckIn(**payload)
        if kind is EventKind.TIMER_FIRE:
            payload["scheduled_for"] = datetime.fromisoformat(payload["scheduled_for"])
            return TimerFire(**payload)
        return UserUtterance(**payload)
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError(f"invalid {value.get('kind', 'unknown')} event payload") from error


def event_to_envelope(event: PersonalEvent) -> ArtifactEnvelope:
    """Wrap one encoded event in a checksummed artifact envelope."""
    return ArtifactEnvelope.create("personal.event", event_to_dict(event))


def event_from_envelope(envelope: ArtifactEnvelope) -> PersonalEvent:
    """Require the personal-event envelope kind before decoding."""
    if envelope.kind != "personal.event":
        raise ValidationError("artifact is not a personal event", path="$.kind")
    return event_from_dict(envelope.payload)


def migrate_legacy_event(value: dict[str, Any]) -> dict[str, Any]:
    """Upgrade the documented schema-zero mapping into schema one."""
    if value.get("schema_version") != 0:
        raise ValidationError("legacy event must have schema version zero")
    migrated: dict[str, Any] = {
        "kind": value.get("type"),
        "schema_version": 1,
        "payload": dict(value.get("data", {})),
    }
    payload: dict[str, Any] = migrated["payload"]
    if migrated["kind"] == EventKind.INBOX_MESSAGE.value:
        payload.setdefault("priority", 0)
    return migrated
