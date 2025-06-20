from __future__ import annotations

from datetime import UTC, datetime

from diurnix.policy import PolicyAction, PolicyEffect
from diurnix.policy_rules import default_personal_policy
from diurnix.tools import SideEffect

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def action(tool: str, capability: str, arguments: dict[str, object]) -> PolicyAction:
    return PolicyAction(tool, (capability,), SideEffect.EXTERNAL, arguments, NOW)


def test_default_policy_allows_reads_and_asks_for_safe_writes() -> None:
    engine = default_personal_policy(("friend@example.test",))
    read = action("calendar.list", "calendar.read", {})
    write = action("mail.send", "mail.send", {"recipients": ["friend@example.test"]})
    assert engine.decide(read).effect is PolicyEffect.ALLOW
    assert engine.decide(write).effect is PolicyEffect.ASK


def test_default_policy_denies_unlisted_recipient_and_unknown_action() -> None:
    engine = default_personal_policy(("friend@example.test",))
    unsafe = action("mail.send", "mail.send", {"recipients": ["other@example.test"]})
    unknown = action("shell.run", "shell.write", {})
    assert engine.decide(unsafe).effect is PolicyEffect.DENY
    assert engine.decide(unknown).effect is PolicyEffect.DENY
