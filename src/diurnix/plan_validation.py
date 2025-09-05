"""Dependency and type validation for the plan DSL."""

from __future__ import annotations

from diurnix.errors import ValidationError
from diurnix.plans import Plan


def validate_references(plan: Plan) -> None:
    steps = {step.step_id: step for step in plan.steps}
    for step in plan.steps:
        for name, ref in step.inputs.items():
            source = steps.get(ref.step_id)
            if source is None:
                raise ValidationError(
                    f"dangling reference: {ref.step_id}",
                    path=f"$.steps.{step.step_id}.inputs.{name}",
                )
            if ref.output not in source.outputs:
                raise ValidationError(
                    f"unknown output: {ref.output}", path=f"$.steps.{step.step_id}.inputs.{name}"
                )
