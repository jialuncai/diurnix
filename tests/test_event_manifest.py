from __future__ import annotations

from datetime import UTC, datetime

from diurnix.event_stream import event_manifest, events_to_jsonl
from diurnix.events import TimerFire
from diurnix.integrity import bytes_checksum

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_event_manifest_hashes_exact_serialized_bytes() -> None:
    events = (TimerFire("timer_1", NOW, "wake", NOW),)
    assert event_manifest(events) == {
        "count": 1,
        "event_ids": ["timer_1"],
        "checksum": bytes_checksum(events_to_jsonl(events).encode("utf-8")),
    }


def test_event_manifest_is_order_sensitive_and_empty_safe() -> None:
    first = TimerFire("timer_1", NOW, "first", NOW)
    second = TimerFire("timer_2", NOW, "second", NOW)
    assert (
        event_manifest((first, second))["checksum"] != event_manifest((second, first))["checksum"]
    )
    empty = event_manifest(())
    assert empty["count"] == 0
    assert empty["checksum"] == bytes_checksum(b"")
