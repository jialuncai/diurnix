"""Declarative tool specifications and strict argument validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from diurnix.errors import ValidationError
from diurnix.identifiers import validate_identifier


class SideEffect(StrEnum):
    """Observable effect class used by policy and execution."""

    NONE = "none"
    LOCAL = "local"
    EXTERNAL = "external"
    MONEY = "money"


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """Portable tool contract independent of an implementation."""

    name: str
    description: str
    arguments: dict[str, Any]
    capabilities: tuple[str, ...]
    side_effect: SideEffect = SideEffect.NONE
    version: int = 1

    def __post_init__(self) -> None:
        validate_identifier(self.name, label="tool name")
        if not self.description.strip():
            raise ValidationError("tool description must not be blank")
        if self.arguments.get("type") != "object":
            raise ValidationError("tool arguments must declare object type")
        if not self.capabilities or len(set(self.capabilities)) != len(self.capabilities):
            raise ValidationError("tool capabilities must be nonempty and unique")
        for capability in self.capabilities:
            validate_identifier(capability, label="capability")
        if self.version < 1:
            raise ValidationError("tool version must be positive")


def validate_arguments(spec: ToolSpec, arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate the supported JSON-schema object subset and return a copy."""
    schema = spec.arguments
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    missing = [name for name in required if name not in arguments]
    if missing:
        raise ValidationError(
            f"missing required arguments: {', '.join(missing)}", path="$.arguments"
        )
    unknown = sorted(set(arguments) - set(properties))
    if unknown and schema.get("additionalProperties", False) is False:
        raise ValidationError(f"unknown arguments: {', '.join(unknown)}", path="$.arguments")
    result = dict(arguments)
    for name, value in arguments.items():
        property_schema = properties.get(name)
        if property_schema is not None:
            _validate_value(value, property_schema, path=f"$.arguments.{name}")
    return result


def _validate_value(value: Any, schema: dict[str, Any], *, path: str) -> None:
    expected = schema.get("type")
    types = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    target = types.get(expected)
    if target is None:
        raise ValidationError(f"unsupported schema type: {expected}", path=path)
    if not isinstance(value, target) or (
        expected in ("integer", "number") and isinstance(value, bool)
    ):
        raise ValidationError(f"expected {expected}", path=path)

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError("value is not in enum", path=path)
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValidationError("string is shorter than minimum", path=path)
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValidationError("string is longer than maximum", path=path)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValidationError("number is below minimum", path=path)
        if "maximum" in schema and value > schema["maximum"]:
            raise ValidationError("number is above maximum", path=path)
