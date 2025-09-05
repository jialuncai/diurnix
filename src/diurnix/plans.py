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
