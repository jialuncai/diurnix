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


def tool_result_to_dict(result: ToolResult) -> dict[str, Any]:
    """Encode a correlated tool result without coercing its output."""
    return {
        "schema_version": 1,
        "call_id": result.call_id,
        "tool": result.tool,
        "output": result.output,
    }


def tool_result_from_dict(value: dict[str, Any]) -> ToolResult:
    """Decode a strict current-version tool result."""
    from diurnix.errors import ValidationError

    if set(value) != {"schema_version", "call_id", "tool", "output"}:
        raise ValidationError("tool result fields do not match schema")
    if value["schema_version"] != 1:
        raise ValidationError("unsupported tool result schema")
    validate_identifier(value["call_id"], label="call_id")
    validate_identifier(value["tool"], label="tool")
    return ToolResult(value["call_id"], value["tool"], value["output"])
