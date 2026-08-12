from __future__ import annotations

from datetime import UTC, datetime

from diurnix.bench import BenchConfig, record_bench_sections
from diurnix.session import SessionReplayer, recorder_from_jsonl_bytes


def test_bench_live_and_replay_bytes_are_identical() -> None:
    config = BenchConfig(3, datetime(2026, 1, 1, tzinfo=UTC))
    sections = ({"app": "inbox", "score": 1.0}, {"app": "ledger", "score": 0.8})
    live = record_bench_sections(config, sections)
    replay = SessionReplayer(recorder_from_jsonl_bytes(live).entries).replay_bytes()
    assert replay == live


def test_same_bench_sections_produce_identical_bytes() -> None:
    config = BenchConfig(3, datetime(2026, 1, 1, tzinfo=UTC))
    sections = ({"app": "calendar", "score": 1.0},)
    assert record_bench_sections(config, sections) == record_bench_sections(config, sections)
