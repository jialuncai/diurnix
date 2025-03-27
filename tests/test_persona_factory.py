from __future__ import annotations

from diurnix.persona_factory import create_persona


def test_persona_factory_is_reproducible_for_same_seed() -> None:
    assert create_persona(17) == create_persona(17)
    assert create_persona(17).persona_id == "persona_286eb51c30a5"


def test_persona_factory_changes_identity_across_seeds() -> None:
    first = create_persona(1)
    second = create_persona(2)
    assert first.persona_id != second.persona_id
    assert first != second


def test_persona_factory_uses_only_synthetic_domains() -> None:
    persona = create_persona(5)
    assert all(item.email.endswith("@example.test") for item in persona.correspondents)
    assert all(item.name.startswith("合成") for item in persona.merchants)
