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


def tool_call_to_dict(call: ToolCall) -> dict[str, Any]:
    """Encode a call into the versioned wire schema."""
    return {
        "schema_version": 1,
        "call_id": call.call_id,
        "tool": call.tool,
        "arguments": dict(call.arguments),
    }


def tool_call_from_dict(value: dict[str, Any]) -> ToolCall:
    """Decode a strict current-version tool call."""
    from diurnix.errors import ValidationError

    if set(value) != {"schema_version", "call_id", "tool", "arguments"}:
        raise ValidationError("tool call fields do not match schema")
    if value["schema_version"] != 1 or not isinstance(value["arguments"], dict):
        raise ValidationError("invalid tool call payload")
    return ToolCall(value["call_id"], value["tool"], dict(value["arguments"]))
