from __future__ import annotations

from datetime import UTC, datetime

from diurnix.codec import canonical_dumps
from diurnix.loop import LoopPhase
from diurnix.traces import LoopTrace, trace_to_dict


def test_trace_mapping_has_stable_entry_shape() -> None:
    trace = LoopTrace().append(LoopPhase.PLAN, datetime(2026, 10, 30, tzinfo=UTC), {"plan": "p"})
    encoded = trace_to_dict(trace)
    assert list(encoded["entries"][0]) == ["sequence", "phase", "occurred_at", "payload"]
    assert '"phase":"plan"' in canonical_dumps(encoded)
