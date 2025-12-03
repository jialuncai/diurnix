from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import SessionRecorder, fork_session


def test_session_fork_can_diverge_after_shared_prefix() -> None:
    source = SessionRecorder()
    source.append("event.user", "t0", {})
    source.append("decision.route", "t1", {"intent": "tasks"})
    branch = fork_session(source.entries, 1)
    branch.append("decision.route", "t1", {"intent": "ledger"})
    assert branch.entries[0] == source.entries[0]
    assert branch.entries[1] != source.entries[1]


def test_session_fork_rejects_unknown_boundary() -> None:
    with pytest.raises(ValidationError, match="boundary"):
        fork_session((), 1)
