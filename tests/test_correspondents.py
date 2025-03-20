from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.persona import Correspondent, validate_correspondents


def test_correspondent_preserves_trust_and_relationship() -> None:
    contact = Correspondent("Lin", "lin@example.test", "classmate", trusted=False)
    assert contact.relationship == "classmate"
    assert contact.trusted is False


def test_correspondent_validates_visible_fields_and_email() -> None:
    with pytest.raises(ValidationError, match="name and relationship"):
        Correspondent(" ", "lin@example.test", "classmate")
    for email in ("lin", "@example.test", "lin@"):
        with pytest.raises(ValidationError, match="email"):
            Correspondent("Lin", email, "classmate")


def test_correspondent_collection_requires_unique_nonempty_emails() -> None:
    first = Correspondent("Lin", "Lin@example.test", "classmate")
    duplicate = Correspondent("Other", "lin@example.test", "neighbor")
    with pytest.raises(ValidationError, match="at least one"):
        validate_correspondents(())
    with pytest.raises(ValidationError, match="unique"):
        validate_correspondents((first, duplicate))
