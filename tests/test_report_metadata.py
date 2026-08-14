from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix import __version__
from diurnix.errors import ValidationError
from diurnix.integrity import content_checksum
from diurnix.reports import build_run_metadata, metadata_to_dict


def test_report_metadata_hashes_actual_config() -> None:
    config = {"seed": 7, "mode": "offline"}
    metadata = build_run_metadata(7, datetime(2026, 10, 30, tzinfo=UTC), config)
    assert metadata.runtime_version == __version__
    assert metadata.config_checksum == content_checksum(config)
    assert metadata.synthetic is True


def test_report_metadata_requires_aware_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        build_run_metadata(1, datetime(2026, 1, 1), {})


def test_report_metadata_mapping_has_stable_schema() -> None:
    encoded = metadata_to_dict(build_run_metadata(1, datetime(2026, 1, 1, tzinfo=UTC), {}))
    assert list(encoded) == [
        "schema_version",
        "seed",
        "generated_at",
        "runtime_version",
        "config_checksum",
        "synthetic",
    ]
