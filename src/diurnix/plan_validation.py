"""Dependency and type validation for the plan DSL."""

from __future__ import annotations

from diurnix.errors import ValidationError
from diurnix.plans import Plan, ValueType


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


def topological_steps(plan: Plan) -> tuple[str, ...]:
    validate_acyclic(plan)
    graph = dependency_graph(plan)
    result = []
    remaining = set(graph)
    while remaining:
        ready = sorted(node for node in remaining if graph[node].isdisjoint(remaining))
        if not ready:
            raise ValidationError("plan dependency cycle")
        result.extend(ready)
        remaining.difference_update(ready)
    return tuple(result)


def validate_types(plan: Plan) -> None:
    validate_references(plan)
    steps = {step.step_id: step for step in plan.steps}
    for step in plan.steps:
        for name, ref in step.inputs.items():
            actual = steps[ref.step_id].outputs[ref.output]
            if ref.value_type is not actual and ValueType.ANY not in (ref.value_type, actual):
                raise ValidationError(
                    f"type mismatch: expected {ref.value_type.value}, got {actual.value}",
                    path=f"$.steps.{step.step_id}.inputs.{name}",
                )


def validate_conditions(plan: Plan, initial: tuple[str, ...] = ()) -> None:
    available = set(initial)
    by_id = {step.step_id: step for step in plan.steps}
    for identity in topological_steps(plan):
        step = by_id[identity]
        missing = sorted(set(step.preconditions) - available)
        if missing:
            raise ValidationError(
                f"unsatisfied preconditions: {', '.join(missing)}",
                path=f"$.steps.{identity}.preconditions",
            )
        available.update(step.effects)


def validate_plan(plan: Plan, initial: tuple[str, ...] = ()) -> None:
    validate_acyclic(plan)
    validate_types(plan)
    validate_conditions(plan, initial)
