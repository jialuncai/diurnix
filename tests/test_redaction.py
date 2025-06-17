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


def test_email_redaction_removes_original_address() -> None:
    from diurnix.redaction import redact_text

    original = "Send to First.Last+tag@example.test now."
    redacted = redact_text(original, kinds=("email",))
    assert redacted == "Send to [EMAIL] now."
    assert "First.Last" not in redacted
    assert "example.test" not in redacted


def test_email_redaction_can_leave_other_kinds_untouched() -> None:
    from diurnix.redaction import redact_text

    text = "a@example.test +86 138 0013 8000"
    assert redact_text(text, kinds=("email",)) == "[EMAIL] +86 138 0013 8000"


def test_phone_and_card_redaction_removes_all_digits() -> None:
    from diurnix.redaction import redact_text

    text = "call +86 138 0013 8000 charge 4111-1111-1111-1111"
    redacted = redact_text(text)
    assert redacted == "call [PHONE] charge [CARD]"
    assert not any(character.isdigit() for character in redacted)


def test_repeated_pii_gets_one_placeholder_per_occurrence() -> None:
    from diurnix.redaction import redact_text

    text = "a@example.test then a@example.test"
    assert redact_text(text).count("[EMAIL]") == 2
    assert "a@example.test" not in redact_text(text)
