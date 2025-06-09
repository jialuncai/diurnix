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
