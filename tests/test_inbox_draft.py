from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.events import InboxLabel, InboxMessage
from diurnix.inbox_app import draft_response, triage_message


def _message(subject: str):
    return InboxMessage(
        "mail",
        datetime(2026, 1, 1, tzinfo=UTC),
        "sender@example.test",
        ("person@example.test",),
        subject,
        "请在周五前确认。",
        InboxLabel.ACTION_REQUIRED,
    )


def test_action_message_gets_deterministic_template_draft() -> None:
    message = _message("请确认时间")
    draft = draft_response(message, triage_message(message))
    assert draft == (
        "主题\N{FULLWIDTH COLON}Re: 请确认时间"
        "\n收件人\N{FULLWIDTH COLON}sender@example.test"
        "\n您好\N{FULLWIDTH COMMA}已收到此合成请求"
        "\N{FULLWIDTH SEMICOLON}请人工确认具体安排。"
    )


def test_draft_rejects_result_from_other_message() -> None:
    message = _message("请确认")
    result = triage_message(message)
    from dataclasses import replace

    with pytest.raises(ValueError, match="another"):
        draft_response(message, replace(result, message_id="other"))


def test_draft_escapes_html_in_subject() -> None:
    message = _message('<script>alert("x")</script> 请确认')
    draft = draft_response(message, triage_message(message))
    assert draft is not None
    assert "<script>" not in draft and "&lt;script&gt;" in draft
    assert "&quot;x&quot;" in draft


def test_non_action_message_has_no_draft() -> None:
    message = InboxMessage(
        "fyi",
        datetime(2026, 1, 1, tzinfo=UTC),
        "sender@example.test",
        ("person@example.test",),
        "项目近况",
        "合成近况",
        InboxLabel.FYI,
    )
    assert draft_response(message, triage_message(message)) is None
