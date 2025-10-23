from __future__ import annotations

from diurnix.router import Intent, extract_features


def test_feature_vector_has_stable_public_schema() -> None:
    vector = extract_features("urgent budget today")
    assert vector.names == (
        *(f"keyword.{intent.value}" for intent in Intent),
        "recurrence",
        "priority",
        "token_count",
    )
    assert len(vector.values) == 8 and vector.values[-1] == 3.0


def test_feature_extraction_is_deterministic() -> None:
    assert extract_features("计划任务") == extract_features("计划任务")
