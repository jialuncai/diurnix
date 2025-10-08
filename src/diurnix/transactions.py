"""Two-phase side-effect commit protocol."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from diurnix.errors import ValidationError
from diurnix.tool_calls import ToolCall


class CommitStatus(StrEnum):
    NEW = "new"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"


@dataclass(frozen=True, slots=True)
class PreparedAction:
    call: ToolCall
    status: CommitStatus = CommitStatus.NEW
    token: str | None = None


def prepare(action: PreparedAction, token: str) -> PreparedAction:
    if action.status is not CommitStatus.NEW:
        raise ValidationError("only new action can prepare")
    if not token:
        raise ValidationError("prepare token must not be empty")
    return replace(action, status=CommitStatus.PREPARED, token=token)


def commit(action: PreparedAction) -> PreparedAction:
    if action.status is not CommitStatus.PREPARED:
        raise ValidationError("only prepared action can commit")
    return replace(action, status=CommitStatus.COMMITTED)


def abort(action: PreparedAction) -> PreparedAction:
    if action.status is CommitStatus.COMMITTED:
        raise ValidationError("committed action cannot abort")
    return replace(action, status=CommitStatus.ABORTED)
