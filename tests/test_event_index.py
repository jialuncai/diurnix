from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.event_index import EventIndex
from diurnix.events import EventKind, TimerFire, UserUtterance

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)
TIMER = TimerFire("timer_1", NOW, "wake", NOW)
UTTERANCE = UserUtterance("utterance_1", NOW + timedelta(seconds=1), "hello", "en-US")


def test_event_index_orders_deduplicates_and_finds_identity() -> None:
    index = EventIndex((UTTERANCE, TIMER, TIMER))
    assert len(index) == 2
    assert index.all() == (TIMER, UTTERANCE)
    assert index.get("timer_1") is TIMER
    assert index.get("missing") is None


def test_event_index_requires_known_identity() -> None:
    index = EventIndex((TIMER,))
    with pytest.raises(ValidationError, match="event not found") as captured:
        index.require("missing")
    assert captured.value.context == {"path": "$.event_id"}


def test_event_index_counts_only_present_families() -> None:
    counts = EventIndex((TIMER, UTTERANCE)).count_by_kind()
    assert counts == {EventKind.TIMER_FIRE: 1, EventKind.USER_UTTERANCE: 1}
    assert EventKind.TRANSACTION not in counts


def test_event_index_rejects_conflicting_identity() -> None:
    conflict = TimerFire("timer_1", NOW + timedelta(seconds=1), "wake", NOW)
    with pytest.raises(ValidationError, match="conflicting event id"):
        EventIndex((TIMER, conflict))


def test_empty_event_index_has_total_read_operations() -> None:
    index = EventIndex(())
    assert len(index) == 0
    assert index.all() == ()
    assert index.count_by_kind() == {}
    assert index.get("anything") is None
