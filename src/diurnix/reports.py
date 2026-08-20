"""Deterministic Markdown, HTML, and SVG report synthesis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from diurnix import __version__
from diurnix.integrity import content_checksum


@dataclass(frozen=True, slots=True)
class RunMetadata:
    seed: int
    generated_at: datetime
    runtime_version: str
    config_checksum: str
    synthetic: bool = True


def build_run_metadata(seed: int, generated_at: datetime, config: dict[str, object]) -> RunMetadata:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        from diurnix.errors import ValidationError

        raise ValidationError("report time must be timezone-aware")
    return RunMetadata(seed, generated_at, __version__, content_checksum(config))


def metadata_to_dict(metadata: RunMetadata) -> dict[str, object]:
    return {
        "schema_version": 1,
        "seed": metadata.seed,
        "generated_at": metadata.generated_at.isoformat(),
        "runtime_version": metadata.runtime_version,
        "config_checksum": metadata.config_checksum,
        "synthetic": metadata.synthetic,
    }


def coverage_limitations(coverage: dict[str, bool]) -> tuple[str, ...]:
    limitations = []
    if coverage.get("synthetic_data", False):
        limitations.append("结果仅来自带种植真值的合成个人数据, 不代表真实人群表现。")
    if not coverage.get("real_llm", False):
        limitations.append("运行仅验证路由、规划、策略与应用算法机制, 未评估真实 LLM 对话能力。")
    if not coverage.get("external_services", False):
        limitations.append("运行未连接网络端点、付费服务或外部数据集。")
    if not coverage.get("torch_models", False):
        limitations.append("本次运行未执行可选的 CPU Torch 训练演示。")
    return tuple(limitations)
