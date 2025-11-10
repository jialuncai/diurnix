from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.session import make_session_entry, session_entry_from_dict, session_entry_to_dict


def test_session_entry_roundtrips_with_checksum() -> None:
    entry = make_session_entry(0, "event.user", "2026-10-30T09:00:00+08:00", {"text": "计划"})
    assert session_entry_from_dict(session_entry_to_dict(entry)) == entry


def test_session_entry_validates_identity_fields() -> None:
    with pytest.raises(ValidationError, match="negative"):
        make_session_entry(-1, "event.user", "now", {})
    with pytest.raises(ValidationError, match="dotted"):
        make_session_entry(0, "event", "now", {})
