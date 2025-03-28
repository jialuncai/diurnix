from __future__ import annotations

from diurnix.events import InboxLabel
from diurnix.synthetic import INBOX_PATTERNS


def test_inbox_pattern_catalog_covers_each_truth_label_once() -> None:
    assert [pattern.label for pattern in INBOX_PATTERNS] == list(InboxLabel)
    assert len({pattern.tell for pattern in INBOX_PATTERNS}) == len(INBOX_PATTERNS)


def test_risky_inbox_patterns_use_untrusted_senders() -> None:
    trust = {pattern.label: pattern.trusted_sender for pattern in INBOX_PATTERNS}
    assert trust[InboxLabel.ACTION_REQUIRED] is True
    assert trust[InboxLabel.FYI] is True
    assert trust[InboxLabel.PHISHING] is False
    assert trust[InboxLabel.SPAM] is False
