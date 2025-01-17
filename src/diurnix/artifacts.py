"""Schema-versioned envelopes shared by persisted runtime artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from diurnix.codec import canonical_dumps, canonical_loads
from diurnix.errors import ValidationError
from diurnix.integrity import content_checksum, verify_content


@dataclass(frozen=True, slots=True)
class ArtifactEnvelope:
    """Immutable payload wrapper whose checksum excludes envelope metadata."""

    kind: str
    schema_version: int
    payload: dict[str, Any]
    checksum: str

    CURRENT_SCHEMA: ClassVar[int] = 1

    @classmethod
    def create(
        cls, kind: str, payload: dict[str, Any], *, schema_version: int = CURRENT_SCHEMA
    ) -> ArtifactEnvelope:
        """Create an envelope after validating its public identifiers."""
        if not kind or not all(part.replace("_", "").isalnum() for part in kind.split(".")):
            raise ValidationError("artifact kind must be a dotted identifier", path="$.kind")
        if schema_version < 1:
            raise ValidationError("schema version must be positive", path="$.schema_version")
        return cls(kind, schema_version, dict(payload), content_checksum(payload))

    def to_dict(self) -> dict[str, Any]:
        """Return the complete versioned wire representation."""
        return {
            "checksum": self.checksum,
            "kind": self.kind,
            "payload": dict(self.payload),
            "schema_version": self.schema_version,
        }

    def to_json(self) -> str:
        """Encode this envelope canonically."""
        return canonical_dumps(self.to_dict())

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ArtifactEnvelope:
        """Decode and verify a strict envelope mapping."""
        required = {"checksum", "kind", "payload", "schema_version"}
        if set(value) != required:
            raise ValidationError("envelope fields do not match schema", path="$")
        if not isinstance(value["payload"], dict):
            raise ValidationError("payload must be an object", path="$.payload")
        if not isinstance(value["kind"], str) or not isinstance(value["schema_version"], int):
            raise ValidationError("envelope metadata has wrong type", path="$")
        if not isinstance(value["checksum"], str):
            raise ValidationError("checksum must be a string", path="$.checksum")
        envelope = cls(
            value["kind"], value["schema_version"], dict(value["payload"]), value["checksum"]
        )
        verify_content(envelope.payload, envelope.checksum)
        return envelope

    @classmethod
    def from_json(cls, text: str) -> ArtifactEnvelope:
        """Decode a canonical JSON object into a verified envelope."""
        value = canonical_loads(text)
        if not isinstance(value, dict):
            raise ValidationError("envelope must be an object", path="$")
        return cls.from_dict(value)
