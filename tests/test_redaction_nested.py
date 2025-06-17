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
