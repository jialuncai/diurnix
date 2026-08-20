from __future__ import annotations

from diurnix.reports import coverage_limitations


def test_limitations_follow_actual_coverage_flags() -> None:
    limitations = coverage_limitations(
        {
            "synthetic_data": True,
            "real_llm": False,
            "external_services": False,
            "torch_models": False,
        }
    )
    assert len(limitations) == 4
    assert "合成个人数据" in limitations[0]
    assert "真实 LLM" in limitations[1]
    assert "CPU Torch" in limitations[3]


def test_full_coverage_flags_only_keep_synthetic_caveat() -> None:
    limitations = coverage_limitations(
        {
            "synthetic_data": True,
            "real_llm": True,
            "external_services": True,
            "torch_models": True,
        }
    )
    assert limitations == ("结果仅来自带种植真值的合成个人数据, 不代表真实人群表现。",)
