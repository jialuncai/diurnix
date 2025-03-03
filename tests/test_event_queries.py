from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.event_stream import events_of_kind
from diurnix.events import EventKind, TimerFire, UserUtterance

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
EVENTS = (
    TimerFire("timer_1", NOW, "wake", NOW),
    UserUtterance("utterance_1", NOW + timedelta(minutes=1), "hello", "en-US"),
    TimerFire("timer_2", NOW + timedelta(minutes=2), "leave", NOW),
)


def test_event_kind_filter_accepts_one_or_many_kinds() -> None:
    assert [event.event_id for event in events_of_kind(EVENTS, EventKind.TIMER_FIRE)] == [
        "timer_1",
        "timer_2",
    ]
    assert events_of_kind(EVENTS, [EventKind.TIMER_FIRE, EventKind.USER_UTTERANCE]) == EVENTS


def test_event_kind_filter_handles_empty_selection_and_generator() -> None:
    assert events_of_kind(EVENTS, []) == ()
    generated = (event for event in EVENTS)
    assert len(events_of_kind(generated, EventKind.TIMER_FIRE)) == 2


def test_time_filter_uses_half_open_boundaries() -> None:
    from diurnix.event_stream import events_between

    selected = events_between(EVENTS, NOW, NOW + timedelta(minutes=2))
    assert [event.event_id for event in selected] == ["timer_1", "utterance_1"]
    assert events_between(EVENTS, NOW, NOW) == ()


def test_time_filter_compares_absolute_instants_across_offsets() -> None:
    from datetime import timezone

    from diurnix.event_stream import events_between

    plus_eight = timezone(timedelta(hours=8))
    local_start = datetime(2026, 10, 30, 16, tzinfo=plus_eight)
    local_end = datetime(2026, 10, 30, 16, 1, tzinfo=plus_eight)
    assert [event.event_id for event in events_between(EVENTS, local_start, local_end)] == [
        "timer_1"
    ]


def test_time_filter_rejects_naive_or_reversed_bounds() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.event_stream import events_between

    with pytest.raises(ValidationError, match="timezone-aware"):
        events_between(EVENTS, datetime(2026, 10, 30), NOW)
    with pytest.raises(ValidationError, match="precedes"):
        events_between(EVENTS, NOW + timedelta(seconds=1), NOW)


def test_event_queries_preserve_original_input_order() -> None:
    from diurnix.event_stream import events_between

    reversed_events = tuple(reversed(EVENTS))
    assert events_between(reversed_events, NOW, NOW + timedelta(hours=1)) == reversed_events
