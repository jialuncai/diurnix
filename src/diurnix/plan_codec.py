"""Canonical mapping codec for plans."""

from __future__ import annotations

from typing import Any

from diurnix.plans import Plan


def plan_to_dict(plan: Plan) -> dict[str, Any]:
    return {
        "schema_version": plan.schema_version,
        "plan_id": plan.plan_id,
        "steps": [
            {
                "step_id": s.step_id,
                "tool": s.tool,
                "arguments": s.arguments,
                "inputs": {
                    k: {"step_id": v.step_id, "output": v.output, "value_type": v.value_type.value}
                    for k, v in s.inputs.items()
                },
                "outputs": {k: v.value for k, v in s.outputs.items()},
                "preconditions": list(s.preconditions),
                "effects": list(s.effects),
                "money_budget": s.money_budget,
            }
            for s in plan.steps
        ],
    }
