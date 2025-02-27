from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.event_stream import events_to_jsonl
from diurnix.events import TimerFire, UserUtterance

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def sample_events() -> list[TimerFire | UserUtterance]:
    return [
        TimerFire("timer_1", NOW, "wake", NOW),
        UserUtterance("utterance_1", NOW + timedelta(seconds=1), "hello", "en-US"),
    ]


def test_jsonl_has_one_canonical_envelope_per_event() -> None:
    text = events_to_jsonl(sample_events())
    assert text.endswith("\n")
    assert len(text.splitlines()) == 2
    assert '"kind":"personal.event"' in text
    assert '"kind":"timer_fire"' in text.splitlines()[0]
    assert '"kind":"user_utterance"' in text.splitlines()[1]


def test_empty_event_sequence_has_empty_byte_representation() -> None:
    assert events_to_jsonl([]) == ""
