from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.event_codec import event_from_dict, migrate_legacy_event
from diurnix.events import InboxLabel, InboxMessage


def legacy_inbox() -> dict[str, object]:
    return {
        "type": "inbox_message",
        "schema_version": 0,
        "data": {
            "event_id": "mail_1",
            "occurred_at": "2026-10-30T08:00:00+00:00",
            "sender": "a@example.test",
            "recipients": ["b@example.test"],
            "subject": "Review",
            "body": "Body",
            "planted_label": "fyi",
        },
    }


def test_legacy_inbox_migration_supplies_priority_default() -> None:
    migrated = migrate_legacy_event(legacy_inbox())
    expected = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Body",
        InboxLabel.FYI,
        0,
    )
    assert event_from_dict(migrated) == expected


def test_legacy_migration_rejects_nonzero_source_version() -> None:
    with pytest.raises(ValidationError, match="version zero"):
        migrate_legacy_event({"schema_version": 1})


def test_legacy_migration_does_not_mutate_nested_data() -> None:
    original = legacy_inbox()
    migrated = migrate_legacy_event(original)
    migrated["payload"]["subject"] = "Changed"
    assert original["data"]["subject"] == "Review"  # type: ignore[index]


def test_legacy_migration_preserves_explicit_priority() -> None:
    original = legacy_inbox()
    original["data"]["priority"] = 3  # type: ignore[index]
    assert migrate_legacy_event(original)["payload"]["priority"] == 3


def test_legacy_unknown_kind_is_rejected_by_typed_decoder() -> None:
    unknown = {"type": "other", "schema_version": 0, "data": {}}
    with pytest.raises(ValidationError, match="invalid other"):
        event_from_dict(migrate_legacy_event(unknown))
