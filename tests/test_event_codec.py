from __future__ import annotations

from datetime import UTC, datetime

from diurnix.codec import canonical_dumps
from diurnix.event_codec import event_to_dict
from diurnix.events import InboxLabel, InboxMessage


def test_inbox_event_has_stable_golden_mapping() -> None:
    event = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Synthetic body",
        InboxLabel.ACTION_REQUIRED,
        2,
    )
    encoded = event_to_dict(event)
    assert canonical_dumps(encoded) == (
        '{"kind":"inbox_message","payload":{"body":"Synthetic body","event_id":"mail_1",'
        '"occurred_at":"2026-10-30T08:00:00+00:00","planted_label":"action_required",'
        '"priority":2,"recipients":["b@example.test"],"sender":"a@example.test",'
        '"subject":"Review"},"schema_version":1}'
    )


def test_event_encoding_returns_fresh_nested_values() -> None:
    event = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Body",
        InboxLabel.FYI,
    )
    encoded = event_to_dict(event)
    encoded["payload"]["recipients"].append("changed@example.test")
    assert event.recipients == ("b@example.test",)
