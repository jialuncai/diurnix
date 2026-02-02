"""Deterministic inbox triage over planted synthetic messages."""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class TriageResult:
    message_id: str
    predicted_label: InboxLabel
    confidence: float
    tells: tuple[str, ...]


def triage_message(message: InboxMessage) -> TriageResult:
    label, tells = classify_inbox(message)
    confidence = 0.98 if tells else 0.6
    return TriageResult(message.event_id, label, confidence, tells)


def triage_inbox(messages: tuple[InboxMessage, ...]) -> tuple[TriageResult, ...]:
    ordered = sorted(messages, key=lambda message: (message.occurred_at, message.event_id))
    return tuple(triage_message(message) for message in ordered)


def triage_metrics(
    messages: tuple[InboxMessage, ...], results: tuple[TriageResult, ...]
) -> dict[str, object]:
    truth = {message.event_id: message.planted_label for message in messages}
    if set(truth) != {result.message_id for result in results}:
        raise ValueError("triage results do not match inbox identities")
    slices = {}
    for label in InboxLabel:
        selected = [result for result in results if truth[result.message_id] is label]
        correct = sum(result.predicted_label is label for result in selected)
        slices[label.value] = {
            "count": len(selected),
            "accuracy": round(correct / len(selected), 6) if selected else 0.0,
        }
    correct = sum(result.predicted_label is truth[result.message_id] for result in results)
    return {
        "sample_count": len(messages),
        "accuracy": round(correct / len(messages), 6) if messages else 0.0,
        "slices": slices,
        "synthetic": True,
    }
