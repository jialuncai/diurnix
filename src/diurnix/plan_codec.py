"""Canonical mapping codec for plans."""

from __future__ import annotations

from typing import Any

from diurnix.errors import ValidationError
from diurnix.plans import InputRef, Plan, PlanStep, ValueType


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


def plan_from_dict(value: dict[str, Any]) -> Plan:
    if set(value) != {"schema_version", "plan_id", "steps"}:
        raise ValidationError("plan fields do not match schema")
    try:
        steps = []
        for item in value["steps"]:
            steps.append(
                PlanStep(
                    item["step_id"],
                    item["tool"],
                    dict(item["arguments"]),
                    {
                        k: InputRef(v["step_id"], v["output"], ValueType(v["value_type"]))
                        for k, v in item["inputs"].items()
                    },
                    {k: ValueType(v) for k, v in item["outputs"].items()},
                    tuple(item["preconditions"]),
                    tuple(item["effects"]),
                    item["money_budget"],
                )
            )
        return Plan(value["plan_id"], tuple(steps), value["schema_version"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid plan payload") from error


def plan_manifest(plan: Plan) -> dict[str, Any]:
    from diurnix.integrity import content_checksum

    encoded = plan_to_dict(plan)
    return {
        "kind": "agent.plan",
        "schema_version": 1,
        "step_count": len(plan.steps),
        "checksum": content_checksum(encoded),
        "plan": encoded,
    }
