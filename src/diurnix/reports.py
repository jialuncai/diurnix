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


def decision_timeline_svg(entries: tuple[object, ...], *, width: int = 640) -> str:
    from html import escape

    if width < 240:
        from diurnix.errors import ValidationError

        raise ValidationError("timeline width is too small")
    height = 50 + len(entries) * 28
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img">'
    ]
    rows.append('<rect width="100%" height="100%" fill="white"/>')
    rows.append('<line x1="30" y1="20" x2="30" y2="100%" stroke="#718096"/>')
    for index, entry in enumerate(entries):
        kind = escape(str(getattr(entry, "kind", "unknown")))
        y = 30 + index * 28
        rows.append(f'<circle cx="30" cy="{y}" r="5" fill="#315f8c"/>')
        rows.append(f'<text x="45" y="{y + 4}" font-size="12">{index}: {kind}</text>')
    rows.append("</svg>")
    return "".join(rows)
