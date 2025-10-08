from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall
from diurnix.transactions import CommitStatus, PreparedAction, prepare


def test_prepare_returns_tokenized_copy() -> None:
    original = PreparedAction(ToolCall("call_1", "mail.send", {}))
    changed = prepare(original, "token")
    assert original.status is CommitStatus.NEW and changed.status is CommitStatus.PREPARED
    assert changed.token == "token"


def test_prepare_rejects_empty_token() -> None:
    with pytest.raises(ValidationError, match="token"):
        prepare(PreparedAction(ToolCall("call_1", "mail.send", {})), "")
