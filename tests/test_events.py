from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import EventKind, PersonalEvent, event_sort_key


@dataclass(frozen=True, slots=True)
class SampleEvent(PersonalEvent):
    KIND = EventKind.TIMER_FIRE


def test_personal_event_exposes_kind_version_and_sort_key() -> None:
    event = SampleEvent("evt_1", datetime(2026, 10, 30, 8, tzinfo=UTC))
    assert event.kind is EventKind.TIMER_FIRE
    assert event.SCHEMA_VERSION == 1
    assert event_sort_key(event) == (event.occurred_at, "evt_1")


def test_personal_event_rejects_nonportable_id() -> None:
    with pytest.raises(ValueError, match="event_id"):
        SampleEvent("Bad ID", datetime(2026, 10, 30, 8, tzinfo=UTC))


def test_personal_event_rejects_naive_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        SampleEvent("evt_1", datetime(2026, 10, 30, 8))


def test_event_kind_wire_values_are_exhaustive() -> None:
    assert [kind.value for kind in EventKind] == [
        "inbox_message",
        "calendar_entry",
        "transaction",
        "habit_check_in",
        "timer_fire",
        "user_utterance",
    ]


def test_event_sort_key_breaks_time_ties_by_identifier() -> None:
    instant = datetime(2026, 10, 30, 8, tzinfo=UTC)
    events = [SampleEvent("evt_b", instant), SampleEvent("evt_a", instant)]
    assert [event.event_id for event in sorted(events, key=event_sort_key)] == ["evt_a", "evt_b"]


def test_event_sort_key_compares_absolute_instants() -> None:
    from datetime import timedelta, timezone

    plus_eight = timezone(timedelta(hours=8))
    later = SampleEvent("evt_a", datetime(2026, 10, 30, 9, tzinfo=plus_eight))
    earlier = SampleEvent("evt_z", datetime(2026, 10, 30, 0, tzinfo=UTC))
    assert sorted([later, earlier], key=event_sort_key) == [earlier, later]
