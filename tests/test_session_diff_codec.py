from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import SessionDifference, difference_from_dict, difference_to_dict


def test_session_difference_mapping_roundtrips_missing_sides() -> None:
    difference = SessionDifference(3, None, "sha256:right")
    assert difference_from_dict(difference_to_dict(difference)) == difference


def test_session_difference_mapping_rejects_extensions() -> None:
    encoded = difference_to_dict(SessionDifference(0, "left", "right"))
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        difference_from_dict(encoded)
