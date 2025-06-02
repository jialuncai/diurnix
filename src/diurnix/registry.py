"""Versioned registry of declarative specs and in-process implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from diurnix.errors import ValidationError
from diurnix.tools import SideEffect, ToolSpec, validate_arguments

ToolImplementation = Callable[[dict[str, Any]], Any]


class ToolRegistry:
    """Deterministic registry keyed by public tool name."""

    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._implementations: dict[str, ToolImplementation] = {}

    def register(self, spec: ToolSpec, implementation: ToolImplementation) -> None:
        """Register a spec and callable atomically without replacement."""
        if spec.name in self._specs:
            raise ValidationError(f"tool is already registered: {spec.name}")
        if not callable(implementation):
            raise ValidationError("tool implementation must be callable")
        self._specs[spec.name] = spec
        self._implementations[spec.name] = implementation

    def get(self, name: str) -> ToolSpec | None:
        """Find a tool spec without exposing registry mappings."""
        return self._specs.get(name)

    def require(self, name: str) -> ToolSpec:
        """Find a tool or raise a precise validation error."""
        spec = self.get(name)
        if spec is None:
            raise ValidationError(f"unknown tool: {name}", path="$.tool")
        return spec

    def names(self) -> tuple[str, ...]:
        """List registered names in lexical order."""
        return tuple(sorted(self._specs))

    def unregister(self, name: str) -> ToolSpec:
        """Remove one registered pair and return its previous spec."""
        spec = self.require(name)
        del self._specs[name]
        del self._implementations[name]
        return spec

    def by_capability(self, capability: str, *, require_all: bool = False) -> tuple[ToolSpec, ...]:
        """Query one capability or a comma-separated conjunction."""
        requested = {item.strip() for item in capability.split(",") if item.strip()}
        if not requested:
            raise ValidationError("capability query must not be empty")
        matches = []
        for spec in self._specs.values():
            available = set(spec.capabilities)
            if requested <= available if require_all else bool(requested & available):
                matches.append(spec)
        return tuple(sorted(matches, key=lambda item: item.name))

    def by_side_effect(self, *effects: SideEffect) -> tuple[ToolSpec, ...]:
        """Return specs matching any requested effect class."""
        accepted = set(effects)
        return tuple(
            sorted(
                (spec for spec in self._specs.values() if spec.side_effect in accepted),
                key=lambda item: item.name,
            )
        )

    def invoke(self, name: str, arguments: dict[str, Any]) -> Any:
        """Validate arguments before calling the bound implementation once."""
        spec = self.require(name)
        validated = validate_arguments(spec, arguments)
        return self._implementations[name](validated)
