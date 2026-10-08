from __future__ import annotations

import os
from pathlib import Path

import pytest
from scripts.check_package import find_wheel


def test_find_wheel_requires_a_built_distribution(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="no diurnix wheel"):
        find_wheel(tmp_path)


def test_find_wheel_selects_the_most_recent_artifact(tmp_path: Path) -> None:
    older = tmp_path / "diurnix-0.1.0-py3-none-any.whl"
    newer = tmp_path / "diurnix-0.1.1-py3-none-any.whl"
    ignored = tmp_path / "another-9.0-py3-none-any.whl"
    for path in (older, newer, ignored):
        path.write_bytes(b"wheel")
    os.utime(older, ns=(1, 1))
    os.utime(newer, ns=(2, 2))
    assert find_wheel(tmp_path) == newer
