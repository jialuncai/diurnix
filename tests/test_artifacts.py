from __future__ import annotations

import pytest

from diurnix.artifacts import ArtifactEnvelope
from diurnix.errors import IntegrityError, ValidationError


def test_artifact_envelope_has_stable_golden_json() -> None:
    envelope = ArtifactEnvelope.create("session.trace", {"seed": 7, "events": []})
    assert envelope.to_json() == (
        '{"checksum":"sha256:a1efbfe0a9bf199909b7cdb8e90aad7d39e3fac230db8cd639a9014e50319836",'
        '"kind":"session.trace","payload":{"events":[],"seed":7},"schema_version":1}'
    )


def test_artifact_envelope_roundtrips_with_integrity_check() -> None:
    original = ArtifactEnvelope.create("memory.note", {"tags": ["home"], "text": "门卡"})
    assert ArtifactEnvelope.from_json(original.to_json()) == original


def test_artifact_envelope_detects_payload_tampering() -> None:
    original = ArtifactEnvelope.create("plan", {"steps": 2}).to_json()
    with pytest.raises(IntegrityError, match="checksum mismatch"):
        ArtifactEnvelope.from_json(original.replace('"steps":2', '"steps":3'))


def test_artifact_kind_and_version_have_strict_bounds() -> None:
    with pytest.raises(ValidationError, match="dotted identifier"):
        ArtifactEnvelope.create("bad kind", {})
    with pytest.raises(ValidationError, match="positive"):
        ArtifactEnvelope.create("plan", {}, schema_version=0)
