from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall, tool_call_from_dict, tool_call_to_dict


def test_tool_call_mapping_roundtrips_with_independent_arguments() -> None:
    call = ToolCall("call_1", "mail.send", {"text": "hello"})
    encoded = tool_call_to_dict(call)
    assert tool_call_from_dict(encoded) == call
    encoded["arguments"]["text"] = "changed"
    assert call.arguments == {"text": "hello"}


def test_tool_call_mapping_rejects_schema_drift() -> None:
    valid = tool_call_to_dict(ToolCall("call_1", "mail.send", {}))
    with pytest.raises(ValidationError, match="fields"):
        tool_call_from_dict({**valid, "extra": True})
    with pytest.raises(ValidationError, match="invalid"):
        tool_call_from_dict({**valid, "schema_version": 2})


def test_tool_result_mapping_roundtrips_nested_output() -> None:
    from diurnix.tool_calls import ToolResult, tool_result_from_dict, tool_result_to_dict

    result = ToolResult("call_1", "mail.send", {"sent": True, "ids": [1, 2]})
    assert tool_result_from_dict(tool_result_to_dict(result)) == result


def test_tool_result_decoder_validates_version_and_identity() -> None:
    from diurnix.tool_calls import ToolResult, tool_result_from_dict, tool_result_to_dict

    valid = tool_result_to_dict(ToolResult("call_1", "mail.send", None))
    with pytest.raises(ValidationError, match="unsupported"):
        tool_result_from_dict({**valid, "schema_version": 2})
    with pytest.raises(ValueError, match="call_id"):
        tool_result_from_dict({**valid, "call_id": "Bad ID"})
