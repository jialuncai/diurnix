from __future__ import annotations

from diurnix.ledger_app import categorize_merchant


def test_merchant_categorizer_supports_synthetic_chinese_names() -> None:
    assert categorize_merchant("合成市场") == ("groceries", ("市场",))
    assert categorize_merchant("合成地铁") == ("transport", ("地铁",))
    assert categorize_merchant("合成视频") == ("subscriptions", ("视频",))


def test_unknown_merchant_uses_explicit_other_category() -> None:
    assert categorize_merchant("Unmapped Shop") == ("other", ())


def test_categorizer_recovers_every_persona_merchant() -> None:
    from diurnix.persona_factory import create_persona

    persona = create_persona(5)
    for merchant in persona.merchants:
        predicted, tells = categorize_merchant(merchant.name)
        assert predicted == merchant.category
        assert tells


def test_categorizer_is_case_insensitive_for_latin_cues() -> None:
    assert categorize_merchant("CITY METRO")[0] == "transport"
