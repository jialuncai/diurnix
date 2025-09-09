from __future__ import annotations

from diurnix.integrity import content_checksum
from diurnix.plan_codec import plan_manifest, plan_to_dict
from diurnix.plans import Plan, PlanStep, ValueType


def test_plan_manifest_covers_exact_plan_mapping() -> None:
    plan = Plan("plan", (PlanStep("now", "clock.now", {}, {}, {"time": ValueType.STRING}),))
    manifest = plan_manifest(plan)
    assert manifest["step_count"] == 1
    assert manifest["checksum"] == content_checksum(plan_to_dict(plan))
