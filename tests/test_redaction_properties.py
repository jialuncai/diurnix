from __future__ import annotations

import random
import string

from diurnix.redaction import contains_pii, redact_value


def test_seeded_random_contexts_never_leak_planted_email() -> None:
    source = random.Random(20261030)
    alphabet = string.ascii_letters + " _-"
    for _ in range(250):
        prefix = "".join(source.choice(alphabet) for _ in range(source.randrange(0, 30)))
        suffix = "".join(source.choice(alphabet) for _ in range(source.randrange(0, 30)))
        email = f"user{source.randrange(10000)}@example.test"
        value = {"nested": [prefix + " " + email + " " + suffix]}
        redacted = redact_value(value)
        assert email not in str(redacted)
        assert not contains_pii(redacted)


def test_seeded_phone_and_card_formats_never_leave_digits() -> None:
    samples = (
        "+86 138 0013 8000",
        "138-0013-8000",
        "4111 1111 1111 1111",
        "5555555555554444",
    )
    for sample in samples:
        redacted = redact_value({"value": sample})["value"]
        assert sample not in redacted
        assert not any(character.isdigit() for character in redacted)
