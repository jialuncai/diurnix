"""Seeded synthetic personal-data generation with planted truth."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from diurnix.events import InboxLabel, InboxMessage
from diurnix.persona import Persona
from diurnix.randomness import SeededRandom


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


def generate_inbox_message(
    persona: Persona, seed: int, index: int, occurred_at: datetime
) -> InboxMessage:
    """Generate one reproducible message and its planted truth label."""
    random = SeededRandom(seed).fork(f"inbox-{index}")
    pattern = random.choice(INBOX_PATTERNS)
    candidates = tuple(
        item for item in persona.correspondents if item.trusted == pattern.trusted_sender
    )
    sender = random.choice(candidates or persona.correspondents)
    return InboxMessage(
        f"mail_{seed}_{index}",
        occurred_at,
        sender.email,
        ("persona@example.test",),
        pattern.subject,
        pattern.body,
        pattern.label,
        3 if pattern.label is InboxLabel.ACTION_REQUIRED else 0,
    )


def generate_inbox_week(
    persona: Persona, seed: int, start: datetime, *, messages_per_day: int = 5
) -> tuple[InboxMessage, ...]:
    """Generate seven ordered local-day batches without network data."""
    if messages_per_day < 1:
        from diurnix.errors import ValidationError

        raise ValidationError("messages per day must be positive")
    result = []
    for day in range(7):
        for slot in range(messages_per_day):
            index = day * messages_per_day + slot
            occurred = start + timedelta(days=day, minutes=slot * 7)
            result.append(generate_inbox_message(persona, seed, index, occurred))
    return tuple(result)


def inbox_ground_truth(messages: tuple[InboxMessage, ...]) -> dict[str, str]:
    """Return event-to-label truth separately from classifier inputs."""
    return {message.event_id: message.planted_label.value for message in messages}


def inbox_label_counts(messages: tuple[InboxMessage, ...]) -> dict[str, int]:
    """Count planted classes in stable enum order, including absent classes."""
    return {
        label.value: sum(message.planted_label is label for message in messages)
        for label in InboxLabel
    }
