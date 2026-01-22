"""Deterministic inbox triage over planted synthetic messages."""

from __future__ import annotations

from diurnix.events import InboxLabel, InboxMessage

_LABEL_CUES = (
    (InboxLabel.PHISHING, ("输入密码", "仿冒链接", "credential", "verify password")),
    (InboxLabel.SPAM, ("大奖", "领取虚构奖品", "unsolicited prize")),
    (InboxLabel.NEWSLETTER, ("取消订阅", "unsubscribe", "每周简报")),
    (InboxLabel.ACTION_REQUIRED, ("请确认", "周五前", "deadline", "action required")),
)


def classify_inbox(message: InboxMessage) -> tuple[InboxLabel, tuple[str, ...]]:
    """Infer a label from literal content without consulting planted truth."""
    text = f"{message.subject}\n{message.body}".casefold()
    for label, cues in _LABEL_CUES:
        matched = tuple(cue for cue in cues if cue in text)
        if matched:
            return label, matched
    return InboxLabel.FYI, ()
