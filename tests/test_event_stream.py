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


def test_event_jsonl_roundtrip_is_byte_stable() -> None:
    from diurnix.event_stream import events_from_jsonl

    encoded = events_to_jsonl(sample_events())
    decoded = events_from_jsonl(encoded)
    assert list(decoded) == sample_events()
    assert events_to_jsonl(decoded) == encoded


def test_empty_event_jsonl_decodes_to_empty_tuple() -> None:
    from diurnix.event_stream import events_from_jsonl

    assert events_from_jsonl("") == ()


def test_event_jsonl_rejects_tampered_payload_checksum() -> None:
    import pytest

    from diurnix.errors import IntegrityError
    from diurnix.event_stream import events_from_jsonl

    encoded = events_to_jsonl(sample_events())
    tampered = encoded.replace("hello", "changed")
    with pytest.raises(IntegrityError, match="checksum mismatch"):
        events_from_jsonl(tampered)


def test_event_jsonl_rejects_blank_record_between_events() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.event_stream import events_from_jsonl

    lines = events_to_jsonl(sample_events()).splitlines()
    with pytest.raises(ValidationError, match="invalid JSON"):
        events_from_jsonl(lines[0] + "\n\n" + lines[1])


def test_event_jsonl_rejects_non_event_envelope() -> None:
    import pytest

    from diurnix.artifacts import ArtifactEnvelope
    from diurnix.errors import ValidationError
    from diurnix.event_stream import events_from_jsonl

    with pytest.raises(ValidationError, match="not a personal event"):
        events_from_jsonl(ArtifactEnvelope.create("plan", {}).to_json())
