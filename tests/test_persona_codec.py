from __future__ import annotations

from diurnix.codec import canonical_dumps
from diurnix.persona_codec import persona_to_dict
from diurnix.persona_factory import create_persona


def test_persona_mapping_contains_every_generation_input() -> None:
    persona = create_persona(3)
    encoded = persona_to_dict(persona)
    assert encoded["schema_version"] == 1
    assert encoded["persona_id"] == persona.persona_id
    assert encoded["work_hours"]["weekdays"] == [0, 1, 2, 3, 4]
    assert len(encoded["correspondents"]) == 3
    assert len(encoded["merchants"]) == 3
    assert len(encoded["habit_goals"]) == 2


def test_persona_mapping_is_canonical_json_compatible() -> None:
    text = canonical_dumps(persona_to_dict(create_persona(3)))
    assert text.startswith('{"correspondents":[')
    assert '"schema_version":1' in text
    assert "example.test" in text
