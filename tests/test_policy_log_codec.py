from __future__ import annotations

from datetime import UTC, datetime

from diurnix.codec import canonical_dumps
from diurnix.policy import PolicyDecision, PolicyEffect
from diurnix.policy_log import DecisionLog, decision_log_to_dict


def test_decision_log_mapping_contains_only_redacted_arguments() -> None:
    decision = PolicyDecision(PolicyEffect.ASK, "mail_ask", "approval", {"to": "[EMAIL]"})
    log = DecisionLog().append(datetime(2026, 10, 30, 8, tzinfo=UTC), "mail.send", decision)
    encoded = decision_log_to_dict(log)
    text = canonical_dumps(encoded)
    assert "[EMAIL]" in text
    assert "example.test" not in text
    assert encoded["records"][0]["sequence"] == 0


def test_empty_decision_log_has_stable_golden_json() -> None:
    assert canonical_dumps(decision_log_to_dict(DecisionLog())) == (
        '{"records":[],"schema_version":1}'
    )


def test_policy_decision_record_schema_is_exhaustive() -> None:
    decision = PolicyDecision(PolicyEffect.DENY, "deny", "blocked", {"to": "[EMAIL]"})
    log = DecisionLog().append(datetime(2026, 10, 30, 8, tzinfo=UTC), "mail.send", decision)
    encoded = decision_log_to_dict(log)
    assert list(encoded) == ["schema_version", "records"]
    assert list(encoded["records"][0]) == [
        "sequence",
        "occurred_at",
        "action_tool",
        "effect",
        "rule_id",
        "reason",
        "redacted_arguments",
    ]


def test_policy_effect_public_wire_order_is_stable() -> None:
    assert [effect.value for effect in PolicyEffect] == ["allow", "ask", "deny"]
