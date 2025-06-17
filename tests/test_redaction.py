from __future__ import annotations

from diurnix.redaction import find_pii


def test_pii_detector_finds_email_phone_and_card_in_order() -> None:
    text = "mail a@example.test phone +86 138 0013 8000 card 4111 1111 1111 1111"
    matches = find_pii(text)
    assert [item.kind for item in matches] == ["email", "phone", "card"]
    assert [item.text for item in matches] == [
        "a@example.test",
        "+86 138 0013 8000",
        "4111 1111 1111 1111",
    ]


def test_pii_detector_ignores_short_numbers_and_broken_addresses() -> None:
    assert find_pii("code 12345; user at example dot test") == ()
    assert [item.kind for item in find_pii("prefix-a@example.test-suffix")] == []
