"""Canonical mapping codec for all built-in personal events."""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Any

from diurnix.events import PersonalEvent


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
