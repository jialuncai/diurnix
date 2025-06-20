from __future__ import annotations

import random
from datetime import UTC, datetime

from diurnix.policy import PolicyAction, PolicyEffect
from diurnix.policy_rules import default_personal_policy
from diurnix.tools import SideEffect


def test_random_unlisted_recipient_sequences_are_always_denied() -> None:
    source = random.Random(20261030)
    engine = default_personal_policy(("safe@example.test",))
    for _index in range(500):
        recipient = f"other{source.randrange(1_000_000)}@example.test"
        action = PolicyAction(
            "mail.send",
            ("mail.send",),
            SideEffect.EXTERNAL,
            {"recipients": [recipient]},
            datetime(2026, 10, 30, 8, tzinfo=UTC),
        )
        decision = engine.decide(action)
        assert decision.effect is PolicyEffect.DENY
        assert decision.rule_id == "recipient_deny"


def test_random_unknown_capabilities_never_pass_default_deny() -> None:
    engine = default_personal_policy(("safe@example.test",))
    for index in range(300):
        action = PolicyAction(
            f"unknown_{index}",
            (f"unknown_{index}.write",),
            SideEffect.EXTERNAL,
            {},
            datetime(2026, 10, 30, 8, tzinfo=UTC),
        )
        assert engine.decide(action).effect is PolicyEffect.DENY
