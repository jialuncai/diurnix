from __future__ import annotations

from datetime import UTC, datetime

from diurnix.factory import SyntheticBundle, audit_bundle, generate_bundle
from diurnix.persona_factory import create_persona


def test_generated_bundle_passes_completeness_audit() -> None:
    bundle = generate_bundle(3, datetime(2026, 10, 1, 8, tzinfo=UTC))
    assert audit_bundle(bundle) == ()


def test_bundle_audit_reports_empty_streams_and_missing_truth() -> None:
    bundle = SyntheticBundle(1, create_persona(1), (), (), (), (), {})
    assert audit_bundle(bundle) == (
        "inbox stream is empty",
        "inbox truth is missing",
        "calendar stream is empty",
        "calendar truth is missing",
        "ledger stream is empty",
        "ledger truth is missing",
        "habits stream is empty",
        "habits truth is missing",
    )
