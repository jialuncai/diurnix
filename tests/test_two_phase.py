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


def test_commit_accepts_only_prepared_action() -> None:
    from diurnix.transactions import commit

    prepared = prepare(PreparedAction(ToolCall("call_1", "mail.send", {})), "token")
    assert commit(prepared).status is CommitStatus.COMMITTED
    with pytest.raises(ValidationError, match="only prepared"):
        commit(PreparedAction(ToolCall("call_2", "mail.send", {})))


def test_abort_handles_new_and_prepared_but_not_committed() -> None:
    from diurnix.transactions import abort, commit

    fresh = PreparedAction(ToolCall("call_1", "mail.send", {}))
    assert abort(fresh).status is CommitStatus.ABORTED
    committed = commit(prepare(fresh, "token"))
    with pytest.raises(ValidationError, match="cannot abort"):
        abort(committed)


def test_commit_status_wire_order_is_stable() -> None:
    assert [status.value for status in CommitStatus] == ["new", "prepared", "committed", "aborted"]


def test_prepared_action_fields_are_exhaustive() -> None:
    from dataclasses import fields

    assert [field.name for field in fields(PreparedAction)] == ["call", "status", "token"]
