"""Deterministic Markdown, HTML, and SVG report synthesis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from diurnix import __version__
from diurnix.integrity import content_checksum


@dataclass(frozen=True, slots=True)
class RunMetadata:
    seed: int
    generated_at: datetime
    runtime_version: str
    config_checksum: str
    synthetic: bool = True


def build_run_metadata(seed: int, generated_at: datetime, config: dict[str, object]) -> RunMetadata:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        from diurnix.errors import ValidationError

        raise ValidationError("report time must be timezone-aware")
    return RunMetadata(seed, generated_at, __version__, content_checksum(config))


def metadata_to_dict(metadata: RunMetadata) -> dict[str, object]:
    return {
        "schema_version": 1,
        "seed": metadata.seed,
        "generated_at": metadata.generated_at.isoformat(),
        "runtime_version": metadata.runtime_version,
        "config_checksum": metadata.config_checksum,
        "synthetic": metadata.synthetic,
    }
