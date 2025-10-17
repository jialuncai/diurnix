from __future__ import annotations

from diurnix.integrity import content_checksum
from diurnix.tool_calls import ToolCall
from diurnix.transactions import PreparedAction, transaction_manifest


def test_transaction_manifest_covers_action_order() -> None:
    actions = (
        PreparedAction(ToolCall("a", "mail.send", {})),
        PreparedAction(ToolCall("b", "mail.send", {})),
    )
    manifest = transaction_manifest(actions)
    assert manifest["action_count"] == 2 and manifest["checksum"] == content_checksum(
        manifest["actions"]
    )
    assert transaction_manifest(tuple(reversed(actions)))["checksum"] != manifest["checksum"]
