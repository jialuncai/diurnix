from __future__ import annotations

import pytest

from diurnix.identifiers import stable_identifier, validate_identifier


def test_identifier_accepts_namespaced_portable_forms() -> None:
    for value in ("event", "session.trace", "tool_name", "plan-step2"):
        assert validate_identifier(value) == value


def test_identifier_rejects_ambiguous_or_nonportable_forms() -> None:
    for value in ("", "Event", "two words", "_hidden", "a..b", "晚餐"):
        with pytest.raises(ValueError, match="portable"):
            validate_identifier(value)


def test_stable_identifier_is_key_order_independent() -> None:
    first = stable_identifier("evt", {"b": 2, "a": 1})
    second = stable_identifier("evt", {"a": 1, "b": 2})
    assert first == second == "evt_43258cff783fe703"


def test_stable_identifier_validates_namespace_and_digest_length() -> None:
    with pytest.raises(ValueError, match="namespace"):
        stable_identifier("Bad Space", {})
    for length in (7, 65):
        with pytest.raises(ValueError, match="8 to 64"):
            stable_identifier("evt", {}, length=length)


def test_identifier_distinguishes_type_and_content_changes() -> None:
    identifiers = {
        stable_identifier("evt", value, length=32)
        for value in (1, "1", [1], {"value": 1}, {"value": 2})
    }
    assert len(identifiers) == 5


def test_identifier_length_controls_only_digest_suffix() -> None:
    short = stable_identifier("receipt", {"tool": "mail"}, length=8)
    long = stable_identifier("receipt", {"tool": "mail"}, length=24)
    assert long.startswith(short)
    assert len(short) == len("receipt_") + 8
    assert len(long) == len("receipt_") + 24
