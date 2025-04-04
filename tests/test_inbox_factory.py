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


def test_single_inbox_generation_is_reproducible() -> None:
    from datetime import UTC, datetime

    from diurnix.persona_factory import create_persona
    from diurnix.synthetic import generate_inbox_message

    persona = create_persona(3)
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    assert generate_inbox_message(persona, 9, 2, now) == generate_inbox_message(persona, 9, 2, now)


def test_inbox_generation_matches_sender_trust_to_pattern() -> None:
    from datetime import UTC, datetime

    from diurnix.events import InboxLabel
    from diurnix.persona_factory import create_persona
    from diurnix.synthetic import generate_inbox_message

    persona = create_persona(3)
    trusted = {item.email: item.trusted for item in persona.correspondents}
    for index in range(30):
        message = generate_inbox_message(persona, 9, index, datetime(2026, 10, 30, 8, tzinfo=UTC))
        expected = message.planted_label not in (InboxLabel.SPAM, InboxLabel.PHISHING)
        assert trusted[message.sender] is expected
