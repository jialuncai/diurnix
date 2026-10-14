from __future__ import annotations

import re
import tomllib
from pathlib import Path

import diurnix

ROOT = Path(__file__).parents[1]


def test_dynamic_version_source_and_changelog_agree() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version_path = Path(project["tool"]["hatch"]["version"]["path"])
    assert version_path == Path("src/diurnix/_version.py")
    source = (ROOT / version_path).read_text(encoding="utf-8")
    match = re.fullmatch(r'__version__ = "([0-9]+\.[0-9]+\.[0-9]+)"\n', source)
    assert match is not None
    assert match.group(1) == diurnix.__version__
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {diurnix.__version__} - " in changelog
