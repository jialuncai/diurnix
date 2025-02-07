from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import EventKind, InboxLabel, InboxMessage

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def message(**changes: object) -> InboxMessage:
    values: dict[str, object] = {
        "event_id": "mail_1",
        "occurred_at": NOW,
        "sender": "alice@example.test",
        "recipients": ("person@example.test",),
        "subject": "Please review",
        "body": "Review the attached synthetic note.",
        "planted_label": InboxLabel.ACTION_REQUIRED,
        "priority": 2,
    }
    values.update(changes)
    return InboxMessage(**values)  # type: ignore[arg-type]


def test_inbox_message_preserves_ground_truth_and_kind() -> None:
    event = message()
    assert event.kind is EventKind.INBOX_MESSAGE
    assert event.planted_label is InboxLabel.ACTION_REQUIRED
    assert event.recipients == ("person@example.test",)


def test_inbox_message_validates_addresses_and_subject() -> None:
    with pytest.raises(ValidationError, match="sender"):
        message(sender="alice")
    with pytest.raises(ValidationError, match="recipients"):
        message(recipients=())
    with pytest.raises(ValidationError, match="subject"):
        message(subject="  ")


def test_inbox_message_priority_includes_both_bounds() -> None:
    assert message(priority=0).priority == 0
    assert message(priority=3).priority == 3
    for invalid in (-1, 4):
        with pytest.raises(ValidationError, match="priority"):
            message(priority=invalid)
