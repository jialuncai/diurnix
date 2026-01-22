from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import InboxLabel, InboxMessage
from diurnix.inbox_app import classify_inbox


def _message(subject: str, body: str, planted: InboxLabel = InboxLabel.FYI):
    return InboxMessage(
        "mail",
        datetime(2026, 1, 1, tzinfo=UTC),
        "sender@example.test",
        ("person@example.test",),
        subject,
        body,
        planted,
    )


def test_inbox_classifier_recognizes_high_risk_cues_first() -> None:
    label, tells = classify_inbox(_message("账户异常", "点击仿冒链接并输入密码。"))
    assert label is InboxLabel.PHISHING
    assert tells == ("输入密码", "仿冒链接")


def test_inbox_classifier_defaults_uncued_content_to_fyi() -> None:
    assert classify_inbox(_message("项目近况", "这是本周的合成近况。")) == (InboxLabel.FYI, ())
