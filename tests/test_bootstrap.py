from __future__ import annotations

import subprocess
import sys

import diurnix
from diurnix.cli import build_parser, main


def test_public_version_is_semantic() -> None:
    major, minor, patch = diurnix.__version__.split(".")
    assert all(part.isdigit() for part in (major, minor, patch))


def test_root_parser_identifies_program() -> None:
    assert build_parser().prog == "diurnix"
    assert main([]) == 0


def test_module_imports_in_fresh_interpreter() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import diurnix; print(diurnix.__version__)"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == diurnix.__version__
