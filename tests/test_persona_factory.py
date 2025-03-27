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


def test_seeded_persona_variant_snapshot() -> None:
    snapshot = [
        (seed, create_persona(seed).name, create_persona(seed).timezone) for seed in range(6)
    ]
    assert snapshot == [
        (0, "方舟", "Europe/Berlin"),
        (1, "周宁", "Europe/Berlin"),
        (2, "方舟", "Asia/Tokyo"),
        (3, "方舟", "Asia/Shanghai"),
        (4, "陈曦", "America/New_York"),
        (5, "陈曦", "America/New_York"),
    ]


def test_seeded_persona_has_required_factory_catalogs() -> None:
    persona = create_persona(9)
    assert len(persona.correspondents) == 3
    assert len(persona.merchants) == 3
    assert len(persona.habit_goals) == 2
    assert {item.trusted for item in persona.correspondents} == {True, False}
