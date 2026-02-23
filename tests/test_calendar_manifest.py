from __future__ import annotations

from datetime import date

from diurnix.calendar_app import calendar_analysis_manifest, propose_conflict_resolutions
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import calendar_week_with_conflict


def test_calendar_manifest_embeds_executed_metrics() -> None:
    persona = create_persona(14)
    entries = calendar_week_with_conflict(persona, 14, date(2026, 10, 26))
    proposals = propose_conflict_resolutions(entries, persona)
    manifest = calendar_analysis_manifest(entries, proposals, 14)
    assert manifest["synthetic"] is True
    assert manifest["proposal_count"] == len(proposals)
    assert manifest["metrics"]["recall"] == 1.0
    assert str(manifest["proposal_checksum"]).startswith("sha256:")
