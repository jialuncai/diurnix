"""Versioned registry of declarative specs and in-process implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from diurnix.errors import ValidationError
from diurnix.tools import ToolSpec

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
