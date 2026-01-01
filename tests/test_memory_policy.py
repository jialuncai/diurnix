from __future__ import annotations

from datetime import UTC, datetime

from diurnix.memory import (
    MemoryScope,
    MemoryStore,
    PrivacyTier,
    make_memory_note,
    policy_read_memory,
)
from diurnix.policy import PolicyEffect, PolicyEngine, PolicyRule


def _store():
    note = make_memory_note(
        "n",
        MemoryScope.PERSISTENT,
        PrivacyTier.SENSITIVE,
        "secret",
        (),
        datetime(2026, 1, 1, tzinfo=UTC),
    )
    return MemoryStore((note,))


def _engine(effect: PolicyEffect):
    rule = PolicyRule(
        "memory-rule", effect, "configured memory rule", capabilities=("memory.read.sensitive",)
    )
    return PolicyEngine((rule,))


def test_policy_allowed_memory_read_returns_note() -> None:
    result = policy_read_memory(
        _store(),
        "n",
        PrivacyTier.SENSITIVE,
        _engine(PolicyEffect.ALLOW),
        datetime(2026, 1, 2, tzinfo=UTC),
    )
    assert result.note is not None and result.policy_effect == "allow"


def test_policy_ask_memory_read_withholds_note() -> None:
    result = policy_read_memory(
        _store(),
        "n",
        PrivacyTier.SENSITIVE,
        _engine(PolicyEffect.ASK),
        datetime(2026, 1, 2, tzinfo=UTC),
    )
    assert result.note is None and result.policy_effect == "ask"


def test_policy_denial_never_returns_stored_content() -> None:
    result = policy_read_memory(
        _store(),
        "n",
        PrivacyTier.SENSITIVE,
        _engine(PolicyEffect.DENY),
        datetime(2026, 1, 2, tzinfo=UTC),
    )
    assert result.note is None
    assert "secret" not in repr(result)


def test_privacy_denial_precedes_allow_policy() -> None:
    result = policy_read_memory(
        _store(),
        "n",
        PrivacyTier.PUBLIC,
        _engine(PolicyEffect.ALLOW),
        datetime(2026, 1, 2, tzinfo=UTC),
    )
    assert result.note is None
    assert result.reason == "privacy tier blocks read"
