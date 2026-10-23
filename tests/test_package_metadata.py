from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _project() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_runtime_and_optional_dependency_boundaries_are_exact() -> None:
    configuration = _project()
    project = configuration["project"]
    assert project["requires-python"] == ">=3.11"
    assert project["dependencies"] == ["numpy>=2.0,<3"]
    assert project["optional-dependencies"]["torch"] == ["torch>=2.4,<3"]
    assert "hatchling>=1.27,<2" in project["optional-dependencies"]["dev"]


def test_build_typing_and_version_metadata_remain_release_compatible() -> None:
    configuration = _project()
    assert configuration["build-system"] == {
        "requires": ["hatchling>=1.27,<2"],
        "build-backend": "hatchling.build",
    }
    assert configuration["tool"]["hatch"]["version"]["path"] == "src/diurnix/_version.py"
    assert "python_version" not in configuration["tool"]["mypy"]
    classifiers = configuration["project"]["classifiers"]
    assert all(
        f"Programming Language :: Python :: {version}" in classifiers
        for version in ("3.11", "3.12", "3.13")
    )
    assert (ROOT / "src" / "diurnix" / "py.typed").is_file()


def test_cpu_index_and_lockfile_are_part_of_the_source_distribution_contract() -> None:
    configuration = _project()
    indexes = configuration["tool"]["uv"]["index"]
    assert indexes == [
        {
            "name": "pytorch-cpu",
            "url": "https://download.pytorch.org/whl/cpu",
            "explicit": True,
        }
    ]
    assert configuration["tool"]["uv"]["sources"]["torch"] == [{"index": "pytorch-cpu"}]
    tracked = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "uv.lock" not in tracked
    assert (ROOT / "uv.lock").is_file()
