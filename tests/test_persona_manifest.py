from __future__ import annotations

from diurnix.integrity import content_checksum
from diurnix.persona_codec import persona_manifest, persona_to_dict
from diurnix.persona_factory import create_persona


def test_persona_manifest_checksum_covers_encoded_inputs() -> None:
    persona = create_persona(7)
    manifest = persona_manifest(persona, seed=7)
    assert manifest["factory"] == "diurnix.synthetic-persona"
    assert manifest["seed"] == 7
    assert manifest["persona_checksum"] == content_checksum(persona_to_dict(persona))


def test_persona_manifest_is_reproducible() -> None:
    assert persona_manifest(create_persona(7), seed=7) == persona_manifest(
        create_persona(7), seed=7
    )
    assert persona_manifest(create_persona(7), seed=7) != persona_manifest(
        create_persona(8), seed=8
    )


def test_persona_manifest_has_stable_top_level_shape() -> None:
    manifest = persona_manifest(create_persona(7), seed=7)
    assert list(manifest) == [
        "factory",
        "factory_version",
        "seed",
        "persona_checksum",
        "persona",
    ]
    assert manifest["factory_version"] == 1
    assert str(manifest["persona_checksum"]).startswith("sha256:")
