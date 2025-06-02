"""Immutable typed values around registry invocation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from diurnix.identifiers import validate_identifier
from diurnix.registry import ToolRegistry


@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    tool: str
    arguments: dict[str, Any]

    def __post_init__(self) -> None:
        validate_identifier(self.call_id, label="call_id")
        validate_identifier(self.tool, label="tool")


@dataclass(frozen=True, slots=True)
class ToolResult:
    call_id: str
    tool: str
    output: Any


def invoke_call(registry: ToolRegistry, call: ToolCall) -> ToolResult:
    """Invoke one typed call and correlate the result by identity."""
    return ToolResult(call.call_id, call.tool, registry.invoke(call.tool, call.arguments))
