from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
LOCAL_LINK = re.compile(r"\[[^]]+\]\((?!https?://|#)([^)]+)\)")


def test_documentation_local_links_resolve() -> None:
    pages = (
        ROOT / "README.md",
        *(ROOT / "docs").glob("*.md"),
        *(ROOT / "examples").rglob("README.md"),
    )
    missing = []
    for page in pages:
        for target in LOCAL_LINK.findall(page.read_text(encoding="utf-8")):
            clean_target = target.split("#", 1)[0]
            if clean_target and not (page.parent / clean_target).resolve().exists():
                missing.append(f"{page.relative_to(ROOT)} -> {target}")
    assert missing == []


def test_example_index_covers_every_executable_walkthrough() -> None:
    index = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    example_directories = {path.parent.name for path in (ROOT / "examples").glob("*/run.py")}
    assert example_directories == {"habit_streak", "ledger_anomaly", "persona_day", "persona_week"}
    assert all(f"{name}/README.md" in index for name in example_directories)


def test_required_timeline_disclosure_is_verbatim() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    disclosure = "".join(
        (
            "本项目于 2026 年 10 月创建和验证。",
            "Git 中 2025 年至 2026 年 10 月的日期是本次生成的演示时间线",
            "\N{FULLWIDTH COMMA}不代表那些日期已经开展的工作。",
            "每次开发提交均执行构建、测试与格式检查",
            "\N{FULLWIDTH SEMICOLON}未使用空提交。",
            "项目未宣称论文成果、预训练模型或真实 LLM 成绩。",
        )
    )
    assert disclosure in readme
