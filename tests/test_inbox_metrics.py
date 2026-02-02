from __future__ import annotations

from datetime import date, time

import pytest

from diurnix.calendar import local_datetime
from diurnix.inbox_app import triage_inbox, triage_metrics
from diurnix.persona_factory import create_persona
from diurnix.synthetic import generate_inbox_week


def _messages():
    persona = create_persona(5)
    start = local_datetime(date(2026, 10, 26), time(9), persona.timezone)
    return generate_inbox_week(persona, 5, start, messages_per_day=2)


def test_triage_metrics_report_synthetic_ground_truth() -> None:
    messages = _messages()
    report = triage_metrics(messages, triage_inbox(messages))
    assert report["synthetic"] is True and report["sample_count"] == 14
    assert report["accuracy"] == 1.0


def test_triage_metrics_reject_mismatched_result_set() -> None:
    with pytest.raises(ValueError, match="identities"):
        triage_metrics(_messages(), ())
