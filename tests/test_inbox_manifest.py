from __future__ import annotations

from datetime import date, time

from diurnix.calendar import local_datetime
from diurnix.inbox_app import triage_inbox, triage_manifest
from diurnix.persona_factory import create_persona
from diurnix.synthetic import generate_inbox_week


def test_triage_manifest_embeds_measured_synthetic_metrics() -> None:
    persona = create_persona(8)
    messages = generate_inbox_week(
        persona,
        8,
        local_datetime(date(2026, 10, 26), time(9), persona.timezone),
        messages_per_day=1,
    )
    manifest = triage_manifest(messages, triage_inbox(messages), 8)
    assert manifest["synthetic"] is True
    assert manifest["metrics"]["sample_count"] == 7
    assert str(manifest["result_checksum"]).startswith("sha256:")
