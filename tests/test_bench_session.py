from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, record_bench_sections
from diurnix.session import recorder_from_jsonl_bytes


def test_bench_session_records_seed_and_sections() -> None:
    config = BenchConfig(2, datetime(2026, 1, 1, tzinfo=UTC))
    content = record_bench_sections(config, ({"app": "inbox", "score": 1.0},))
    entries = recorder_from_jsonl_bytes(content).entries
    assert tuple(entry.kind for entry in entries) == ("event.bench", "observation.inbox")
    assert entries[0].payload == {"seed": 2}


def test_empty_bench_sections_still_record_run_identity() -> None:
    config = BenchConfig(2, datetime(2026, 1, 1, tzinfo=UTC))
    assert len(recorder_from_jsonl_bytes(record_bench_sections(config, ())).entries) == 1
