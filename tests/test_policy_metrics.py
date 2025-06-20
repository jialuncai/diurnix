from __future__ import annotations

from datetime import UTC, datetime

from diurnix.policy import PolicyDecision, PolicyEffect
from diurnix.policy_log import DecisionLog, decision_metrics

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_decision_metrics_count_effects_and_rules() -> None:
    log = DecisionLog()
    for index, effect in enumerate((PolicyEffect.ALLOW, PolicyEffect.DENY, PolicyEffect.DENY)):
        log = log.append(
            NOW,
            f"tool_{index}",
            PolicyDecision(
                effect, "deny" if effect is PolicyEffect.DENY else "allow", "reason", {}
            ),
        )
    assert decision_metrics(log) == {
        "decision_count": 3,
        "effects": {"allow": 1, "ask": 0, "deny": 2},
        "rules": {"allow": 1, "deny": 2},
    }


def test_empty_decision_metrics_keep_effect_schema() -> None:
    assert decision_metrics(DecisionLog()) == {
        "decision_count": 0,
        "effects": {"allow": 0, "ask": 0, "deny": 0},
        "rules": {},
    }
