from __future__ import annotations

from datetime import date

from diurnix.calendar_app import proposal_from_dict, proposal_to_dict, propose_reschedule
from diurnix.persona_factory import create_persona
from diurnix.synthetic_calendar import generate_calendar_entry


def _proposal():
    persona = create_persona(6)
    source = generate_calendar_entry(persona, 6, 0, date(2026, 10, 26))
    proposal = propose_reschedule(source, (), persona, date(2026, 10, 27))
    assert proposal is not None
    return proposal


def test_calendar_proposal_mapping_roundtrips() -> None:
    proposal = _proposal()
    assert proposal_from_dict(proposal_to_dict(proposal)) == proposal


def test_calendar_proposal_mapping_has_golden_keys() -> None:
    assert list(proposal_to_dict(_proposal())) == [
        "schema_version",
        "entry_id",
        "starts_at",
        "ends_at",
        "reason",
    ]


def test_calendar_proposal_rejects_unknown_fields() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = proposal_to_dict(_proposal())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        proposal_from_dict(encoded)


def test_calendar_proposal_rejects_reversed_bounds() -> None:
    import pytest

    from diurnix.errors import ValidationError

    encoded = proposal_to_dict(_proposal())
    encoded["ends_at"] = encoded["starts_at"]
    with pytest.raises(ValidationError, match="bounds"):
        proposal_from_dict(encoded)
