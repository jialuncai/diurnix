from __future__ import annotations

from diurnix.redaction import contains_pii, redact_value


def test_nested_redaction_preserves_shape_and_nonstring_values() -> None:
    value = {
        "to": ["a@example.test"],
        "metadata": {"phone": "+86 138 0013 8000", "urgent": True},
        "count": 2,
    }
    assert contains_pii(value)
    redacted = redact_value(value)
    assert redacted == {
        "to": ["[EMAIL]"],
        "metadata": {"phone": "[PHONE]", "urgent": True},
        "count": 2,
    }
    assert not contains_pii(redacted)


def test_nested_redaction_does_not_mutate_source() -> None:
    value = {"items": ("a@example.test", "safe")}
    redacted = redact_value(value)
    assert value == {"items": ("a@example.test", "safe")}
    assert redacted == {"items": ("[EMAIL]", "safe")}


def test_redaction_is_idempotent_in_both_directions() -> None:
    value = {"mail": "a@example.test", "safe": "hello", "number": 3}
    once = redact_value(value)
    twice = redact_value(once)
    assert twice == once
    assert redact_value({"safe": "hello"}) == {"safe": "hello"}


def test_contains_pii_agrees_before_and_after_transform() -> None:
    planted = ["a@example.test", "+86 138 0013 8000", "4111111111111111"]
    for text in planted:
        assert contains_pii(text)
        assert not contains_pii(redact_value(text))
