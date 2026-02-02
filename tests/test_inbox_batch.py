from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.events import InboxLabel, InboxMessage
from diurnix.inbox_app import triage_inbox


def _message(message_id: str, minute: int):
    occurred = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=minute)
    return InboxMessage(
        message_id,
        occurred,
        "sender@example.test",
        ("person@example.test",),
        "项目近况",
        "合成近况",
        InboxLabel.FYI,
    )


def test_inbox_batch_is_sorted_by_time_then_id() -> None:
    results = triage_inbox((_message("z", 1), _message("b", 0), _message("a", 0)))
    assert tuple(result.message_id for result in results) == ("a", "b", "z")


def test_empty_inbox_has_empty_triage() -> None:
    assert triage_inbox(()) == ()
