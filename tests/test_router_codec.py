from __future__ import annotations

from diurnix.router import Intent, NumpyRouter, route_to_dict


def test_route_mapping_has_every_intent_score() -> None:
    encoded = route_to_dict(NumpyRouter().route("budget"))
    assert list(encoded) == ["schema_version", "intent", "scores", "ambiguous"]
    assert list(encoded["scores"]) == [intent.value for intent in Intent]


def test_route_mapping_roundtrips() -> None:
    from diurnix.router import route_from_dict

    result = NumpyRouter().route("task 任务")
    assert route_from_dict(route_to_dict(result)) == result
