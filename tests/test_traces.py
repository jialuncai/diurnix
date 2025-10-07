from __future__ import annotations

from datetime import UTC, datetime

from diurnix.loop import LoopPhase
from diurnix.traces import LoopTrace


def test_loop_trace_appends_immutable_sequences() -> None:
    empty = LoopTrace()
    first = empty.append(LoopPhase.PERCEIVE, datetime(2026, 10, 30, tzinfo=UTC), {"event": 1})
    assert empty.entries == () and first.entries[0].sequence == 0
    assert first.entries[0].payload == {"event": 1}
