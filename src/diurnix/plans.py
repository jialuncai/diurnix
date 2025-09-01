"""Versioned typed plan DSL and deterministic dependency validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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
