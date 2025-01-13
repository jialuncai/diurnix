"""Structured public errors with machine-readable context."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class DiurnixError(Exception):
    """Base error carrying a stable code and immutable display context."""

    message: str
    code: str = "runtime_error"
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)
        self.context = dict(self.context)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible error description."""
        return {"code": self.code, "message": self.message, "context": dict(self.context)}


class ValidationError(DiurnixError):
    """Input violates a declared runtime contract."""

    def __init__(self, message: str, *, path: str = "$") -> None:
        super().__init__(message, "validation_error", {"path": path})


class IntegrityError(DiurnixError):
    """Serialized content does not match its checksum or envelope."""

    def __init__(self, message: str, *, expected: str, actual: str) -> None:
        super().__init__(message, "integrity_error", {"expected": expected, "actual": actual})
