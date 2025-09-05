from __future__ import annotations

from diurnix.codec import canonical_dumps
from diurnix.plan_codec import plan_to_dict
from diurnix.plans import Plan, PlanStep, ValueType


def sample() -> Plan:
    return Plan("plan_1", (PlanStep("now", "clock.now", {}, {}, {"time": ValueType.STRING}),))


def test_plan_mapping_is_versioned_and_complete() -> None:
    encoded = plan_to_dict(sample())
    assert list(encoded) == ["schema_version", "plan_id", "steps"]
    assert encoded["steps"][0]["outputs"] == {"time": "string"}


def test_plan_mapping_has_stable_canonical_bytes() -> None:
    assert canonical_dumps(plan_to_dict(sample())).startswith(
        '{"plan_id":"plan_1","schema_version":1'
    )
