"""Deterministic planner over registered tool capabilities."""

from __future__ import annotations

from diurnix.errors import ValidationError
from diurnix.identifiers import stable_identifier
from diurnix.plans import Plan, PlanStep, ValueType
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


class DeterministicPlanner:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def resolve(self, capability: str) -> ToolSpec:
        matches = self.registry.by_capability(capability, require_all=True)
        if not matches:
            raise ValidationError(f"no tool for capability: {capability}")
        if len(matches) > 1:
            raise ValidationError(f"ambiguous tools for capability: {capability}")
        return matches[0]

    def plan(self, capabilities: tuple[str, ...]) -> Plan:
        if not capabilities:
            raise ValidationError("planner requires goals")
        steps = []
        for index, capability in enumerate(capabilities):
            spec = self.resolve(capability)
            steps.append(PlanStep(f"step_{index}", spec.name, {}, {}, {"result": ValueType.ANY}))
        identity = stable_identifier("plan", {"capabilities": list(capabilities)})
        return Plan(identity, tuple(steps))

    def chained_plan(self, capabilities: tuple[str, ...]) -> Plan:
        from diurnix.plans import InputRef

        base = self.plan(capabilities)
        steps = []
        for index, step in enumerate(base.steps):
            inputs = (
                {}
                if index == 0
                else {"previous": InputRef(f"step_{index - 1}", "result", ValueType.ANY)}
            )
            steps.append(PlanStep(step.step_id, step.tool, step.arguments, inputs, step.outputs))
        return Plan(base.plan_id, tuple(steps))


def replace_step_tool(plan: Plan, step_id: str, tool: str) -> Plan:
    if not any(step.step_id == step_id for step in plan.steps):
        raise ValidationError(f"unknown plan step: {step_id}")
    steps = tuple(
        PlanStep(
            step.step_id,
            tool if step.step_id == step_id else step.tool,
            step.arguments,
            step.inputs,
            step.outputs,
            step.preconditions,
            step.effects,
            step.money_budget,
        )
        for step in plan.steps
    )
    return Plan(plan.plan_id, steps)


def violated_preconditions(step: PlanStep, observed: tuple[str, ...]) -> tuple[str, ...]:
    available = set(observed)
    return tuple(item for item in step.preconditions if item not in available)


def allocate_money_budget(plan: Plan, total: float) -> Plan:
    if total < 0:
        raise ValidationError("plan budget cannot be negative")
    share = round(total / len(plan.steps), 6)
    remaining = round(total - share * (len(plan.steps) - 1), 6)
    steps = []
    for index, step in enumerate(plan.steps):
        amount = remaining if index == len(plan.steps) - 1 else share
        steps.append(
            PlanStep(
                step.step_id,
                step.tool,
                step.arguments,
                step.inputs,
                step.outputs,
                step.preconditions,
                step.effects,
                amount,
            )
        )
    return Plan(plan.plan_id, tuple(steps))
