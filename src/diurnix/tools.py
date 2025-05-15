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
