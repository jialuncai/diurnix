from __future__ import annotations

from diurnix.events import InboxLabel
from diurnix.inbox_app import TriageResult, triage_action


def test_each_triage_label_has_one_safe_action() -> None:
    expected = {
        "action_required": "draft_for_approval",
        "fyi": "archive",
        "newsletter": "read_later",
        "spam": "discard",
        "phishing": "quarantine",
    }
    actual = {label.value: triage_action(TriageResult("m", label, 1.0, ())) for label in InboxLabel}
    assert actual == expected


def test_high_risk_labels_never_map_to_send() -> None:
    for label in (InboxLabel.SPAM, InboxLabel.PHISHING):
        assert "send" not in triage_action(TriageResult("m", label, 1.0, ()))
