"""Seeded synthetic personal-data generation with planted truth."""

from __future__ import annotations

from dataclasses import dataclass

from diurnix.events import InboxLabel


@dataclass(frozen=True, slots=True)
class InboxPattern:
    """Original synthetic template with an explicit truth label and tell."""

    label: InboxLabel
    subject: str
    body: str
    tell: str
    trusted_sender: bool


INBOX_PATTERNS = (
    InboxPattern(InboxLabel.ACTION_REQUIRED, "请确认时间", "请在周五前确认。", "deadline", True),
    InboxPattern(InboxLabel.FYI, "项目近况", "这是本周的合成近况。", "informational", True),
    InboxPattern(InboxLabel.NEWSLETTER, "每周简报", "取消订阅 | 合成内容", "unsubscribe", True),
    InboxPattern(InboxLabel.SPAM, "限时大奖", "立即领取虚构奖品。", "unsolicited prize", False),
    InboxPattern(
        InboxLabel.PHISHING, "账户异常", "点击仿冒链接并输入密码。", "credential request", False
    ),
)
