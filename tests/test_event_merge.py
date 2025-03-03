from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.event_stream import deduplicate_events
from diurnix.events import TimerFire

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
FIRST = TimerFire("timer_1", NOW, "wake", NOW)
SECOND = TimerFire("timer_2", NOW + timedelta(minutes=1), "leave", NOW)


def test_event_deduplication_keeps_first_occurrence_order() -> None:
    assert deduplicate_events((FIRST, SECOND, FIRST)) == (FIRST, SECOND)


def test_event_deduplication_rejects_id_content_conflict() -> None:
    conflict = TimerFire("timer_1", NOW + timedelta(seconds=1), "wake", NOW)
    with pytest.raises(ValidationError, match="conflicting event id") as captured:
        deduplicate_events((FIRST, conflict))
    assert captured.value.context == {"path": "$.event_id"}


def test_event_deduplication_accepts_empty_iterable() -> None:
    assert deduplicate_events(event for event in ()) == ()
