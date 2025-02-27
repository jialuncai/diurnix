from __future__ import annotations

from datetime import UTC, datetime

from diurnix.event_stream import append_event, events_to_jsonl, read_event_file
from diurnix.events import TimerFire, UserUtterance

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_append_event_preserves_existing_records(tmp_path: object) -> None:
    from pathlib import Path

    root = Path(str(tmp_path))
    path = root / "nested" / "events.jsonl"
    first = TimerFire("timer_1", NOW, "wake", NOW)
    second = UserUtterance("utterance_1", NOW, "hello", "en-US")
    append_event(path, first)
    first_bytes = path.read_bytes()
    append_event(path, second)
    assert path.read_bytes().startswith(first_bytes)
    assert read_event_file(path) == (first, second)
    assert path.read_text(encoding="utf-8") == events_to_jsonl((first, second))


def test_missing_event_file_reads_as_empty(tmp_path: object) -> None:
    from pathlib import Path

    assert read_event_file(Path(str(tmp_path)) / "missing.jsonl") == ()
