from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import InboxLabel, InboxMessage
from diurnix.inbox_app import triage_message


def _message(subject: str, body: str):
    return InboxMessage(
        "mail-1",
        datetime(2026, 1, 1, tzinfo=UTC),
        "sender@example.test",
        ("person@example.test",),
        subject,
        body,
        InboxLabel.FYI,
    )


def test_triage_result_exposes_evidence_and_confidence() -> None:
    result = triage_message(_message("请确认时间", "请在周五前确认。"))
    assert result.message_id == "mail-1"
    assert result.predicted_label is InboxLabel.ACTION_REQUIRED
    assert result.confidence == 0.98 and result.tells


def test_uncued_triage_has_honest_lower_confidence() -> None:
    result = triage_message(_message("近况", "合成信息"))
    assert result.predicted_label is InboxLabel.FYI
    assert result.confidence == 0.6 and result.tells == ()
