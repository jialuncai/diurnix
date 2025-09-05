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


def dependency_graph(plan: Plan) -> dict[str, set[str]]:
    return {step.step_id: {ref.step_id for ref in step.inputs.values()} for step in plan.steps}


def validate_acyclic(plan: Plan) -> None:
    validate_references(plan)
    graph = dependency_graph(plan)
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValidationError(f"plan dependency cycle at {node}")
        if node in done:
            return
        visiting.add(node)
        for dep in sorted(graph[node]):
            visit(dep)
        visiting.remove(node)
        done.add(node)

    for node in sorted(graph):
        visit(node)
