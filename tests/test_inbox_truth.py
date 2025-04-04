from __future__ import annotations

from datetime import UTC, datetime

from diurnix.events import InboxLabel
from diurnix.persona_factory import create_persona
from diurnix.synthetic import generate_inbox_week, inbox_ground_truth, inbox_label_counts


def test_inbox_truth_maps_every_generated_identity() -> None:
    messages = generate_inbox_week(
        create_persona(2), 5, datetime(2026, 10, 26, 8, tzinfo=UTC), messages_per_day=2
    )
    truth = inbox_ground_truth(messages)
    assert list(truth) == [message.event_id for message in messages]
    assert set(truth.values()) <= {label.value for label in InboxLabel}


def test_inbox_label_counts_include_absent_classes() -> None:
    messages = generate_inbox_week(
        create_persona(2), 5, datetime(2026, 10, 26, 8, tzinfo=UTC), messages_per_day=1
    )
    counts = inbox_label_counts(messages)
    assert list(counts) == [label.value for label in InboxLabel]
    assert sum(counts.values()) == 7
