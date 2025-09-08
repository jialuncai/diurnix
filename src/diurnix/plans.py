"""Versioned typed plan DSL and deterministic dependency validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from diurnix.errors import ValidationError


class ValueType(StrEnum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"


@dataclass(frozen=True, slots=True)
class InputRef:
    step_id: str
    output: str
    value_type: ValueType = ValueType.ANY

    def __post_init__(self) -> None:
        from diurnix.identifiers import validate_identifier

        validate_identifier(self.step_id, label="step_id")
        validate_identifier(self.output, label="output")


@dataclass(frozen=True, slots=True)
class PlanStep:
    step_id: str
    tool: str
    arguments: dict[str, Any]
    inputs: dict[str, InputRef]
    outputs: dict[str, ValueType]
    preconditions: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    money_budget: float = 0.0

    def __post_init__(self) -> None:
        from diurnix.identifiers import validate_identifier

        validate_identifier(self.step_id, label="step_id")
        validate_identifier(self.tool, label="tool")
        if not self.outputs:
            raise ValidationError("plan step requires outputs")
        if self.money_budget < 0:
            raise ValidationError("step money budget cannot be negative")
        for name in (*self.inputs, *self.outputs):
            validate_identifier(name, label="port")


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: str
    steps: tuple[PlanStep, ...]
    schema_version: int = 1

    def __post_init__(self) -> None:
        from diurnix.identifiers import validate_identifier

        validate_identifier(self.plan_id, label="plan_id")
        if self.schema_version != 1:
            raise ValidationError("unsupported plan schema version")
        if not self.steps:
            raise ValidationError("plan requires at least one step")
        ids = [step.step_id for step in self.steps]
        if len(set(ids)) != len(ids):
            raise ValidationError("plan step IDs must be unique")

    @property
    def total_money_budget(self) -> float:
        return round(sum(step.money_budget for step in self.steps), 6)


def diff_plans(before: Plan, after: Plan) -> dict[str, tuple[str, ...]]:
    old = {step.step_id: step for step in before.steps}
    new = {step.step_id: step for step in after.steps}
    return {
        "added": tuple(sorted(set(new) - set(old))),
        "removed": tuple(sorted(set(old) - set(new))),
        "changed": tuple(sorted(key for key in set(old) & set(new) if old[key] != new[key])),
    }
