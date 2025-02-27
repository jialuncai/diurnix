from __future__ import annotations

from datetime import UTC, datetime

from diurnix.codec import canonical_dumps
from diurnix.event_codec import event_to_dict
from diurnix.events import InboxLabel, InboxMessage


def test_inbox_event_has_stable_golden_mapping() -> None:
    event = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Synthetic body",
        InboxLabel.ACTION_REQUIRED,
        2,
    )
    encoded = event_to_dict(event)
    assert canonical_dumps(encoded) == (
        '{"kind":"inbox_message","payload":{"body":"Synthetic body","event_id":"mail_1",'
        '"occurred_at":"2026-10-30T08:00:00+00:00","planted_label":"action_required",'
        '"priority":2,"recipients":["b@example.test"],"sender":"a@example.test",'
        '"subject":"Review"},"schema_version":1}'
    )


def test_event_encoding_returns_fresh_nested_values() -> None:
    event = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Body",
        InboxLabel.FYI,
    )
    encoded = event_to_dict(event)
    encoded["payload"]["recipients"].append("changed@example.test")
    assert event.recipients == ("b@example.test",)


def test_every_event_family_roundtrips_through_typed_union() -> None:
    from datetime import timedelta

    from diurnix.event_codec import event_from_dict
    from diurnix.events import (
        AnomalyLabel,
        CalendarEntry,
        HabitCheckIn,
        HabitStatus,
        TimerFire,
        Transaction,
        UserUtterance,
    )

    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    events = [
        InboxMessage("mail_1", now, "a@x.test", ("b@x.test",), "s", "b", InboxLabel.FYI),
        CalendarEntry("cal_1", now, "meeting", now, now + timedelta(hours=1)),
        Transaction("txn_1", now, -2.0, "CNY", "shop", "food", AnomalyLabel.NONE),
        HabitCheckIn("habit_1", now, "walk", "2026-10-30", HabitStatus.DONE),
        TimerFire("timer_1", now, "wake", now),
        UserUtterance("utterance_1", now, "hello", "en-US"),
    ]
    for event in events:
        assert event_from_dict(event_to_dict(event)) == event


def test_event_decoder_rejects_schema_drift() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.event_codec import event_from_dict

    with pytest.raises(ValidationError, match="fields"):
        event_from_dict({"kind": "timer_fire", "schema_version": 1, "payload": {}, "extra": 1})
    with pytest.raises(ValidationError, match="unsupported"):
        event_from_dict({"kind": "timer_fire", "schema_version": 2, "payload": {}})
    with pytest.raises(ValidationError, match="must be an object"):
        event_from_dict({"kind": "timer_fire", "schema_version": 1, "payload": []})


def test_event_decoder_wraps_unknown_kind_and_missing_fields() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.event_codec import event_from_dict

    with pytest.raises(ValidationError, match="invalid unknown_kind"):
        event_from_dict({"kind": "unknown_kind", "schema_version": 1, "payload": {}})
    with pytest.raises(ValidationError, match="invalid timer_fire"):
        event_from_dict({"kind": "timer_fire", "schema_version": 1, "payload": {}})


def test_event_integrity_envelope_roundtrips_and_detects_wrong_kind() -> None:
    import pytest

    from diurnix.artifacts import ArtifactEnvelope
    from diurnix.errors import ValidationError
    from diurnix.event_codec import event_from_envelope, event_to_envelope

    event = InboxMessage(
        "mail_1",
        datetime(2026, 10, 30, 8, tzinfo=UTC),
        "a@example.test",
        ("b@example.test",),
        "Review",
        "Body",
        InboxLabel.FYI,
    )
    assert (
        event_from_envelope(ArtifactEnvelope.from_json(event_to_envelope(event).to_json())) == event
    )
    wrong = ArtifactEnvelope.create("plan", event_to_dict(event))
    with pytest.raises(ValidationError, match="not a personal event"):
        event_from_envelope(wrong)
