from __future__ import annotations

from diurnix.tool_calls import ToolCall
from diurnix.transactions import PreparedAction, action_to_dict, prepare


def test_prepared_action_mapping_records_phase_token() -> None:
    action = prepare(PreparedAction(ToolCall("call_1", "mail.send", {})), "token")
    assert (
        action_to_dict(action)["status"] == "prepared"
        and action_to_dict(action)["token"] == "token"
    )
