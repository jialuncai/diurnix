from __future__ import annotations

from datetime import UTC, datetime

from diurnix.integrity import content_checksum
from diurnix.loop import LoopPhase
from diurnix.traces import LoopTrace, trace_manifest


def test_trace_manifest_covers_exact_trace() -> None:
    trace = LoopTrace().append(LoopPhase.PERCEIVE, datetime(2026, 10, 30, tzinfo=UTC), {})
    manifest = trace_manifest(trace)
    assert manifest["entry_count"] == 1 and manifest["checksum"] == content_checksum(
        manifest["trace"]
    )
