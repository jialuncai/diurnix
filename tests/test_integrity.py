from __future__ import annotations

import pytest

from diurnix.errors import IntegrityError, ValidationError
from diurnix.integrity import bytes_checksum, content_checksum, verify_content


def test_bytes_checksum_has_algorithm_prefix_and_known_digest() -> None:
    assert bytes_checksum(b"diurnix") == (
        "sha256:e78d6cc3f58112f2efad43d65b3029082879b4598936a62efc5ba1bc07e4cc4a"
    )


def test_semantically_identical_mapping_content_has_identical_checksum() -> None:
    assert content_checksum({"b": 2, "a": 1}) == content_checksum({"a": 1, "b": 2})


def test_verify_content_accepts_match_and_rejects_tampering() -> None:
    checksum = content_checksum({"count": 3})
    assert verify_content({"count": 3}, checksum) is None
    with pytest.raises(IntegrityError) as captured:
        verify_content({"count": 4}, checksum)
    assert captured.value.context["expected"] == checksum
    assert captured.value.context["actual"] == content_checksum({"count": 4})


def test_verify_content_rejects_malformed_digest_first() -> None:
    with pytest.raises(ValidationError, match="64 lowercase"):
        verify_content({}, "sha256:ABC")
