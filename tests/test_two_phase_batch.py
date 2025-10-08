from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall
from diurnix.transactions import CommitStatus, PreparedAction, commit_batch, prepare_batch


def test_two_phase_batch_commits_only_after_all_prepare() -> None:
    actions = tuple(PreparedAction(ToolCall(f"call_{i}", "mail.send", {})) for i in range(3))
    prepared = prepare_batch(actions)
    committed = commit_batch(prepared)
    assert all(item.status is CommitStatus.COMMITTED for item in committed)
    assert all(item.status is CommitStatus.NEW for item in actions)


def test_two_phase_batch_rejects_duplicate_identity() -> None:
    action = PreparedAction(ToolCall("same", "mail.send", {}))
    with pytest.raises(ValidationError, match="unique"):
        prepare_batch((action, action))
