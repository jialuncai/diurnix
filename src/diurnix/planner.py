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
