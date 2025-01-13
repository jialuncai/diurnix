"""Smoke-check an installed wheel and its console entry point."""

from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> int:
    """Import the installed package and invoke the command help."""
    subprocess.run([sys.executable, "-c", "import diurnix; print(diurnix.__version__)"], check=True)
    executable = shutil.which("diurnix")
    if executable is None:
        raise RuntimeError("diurnix console entry point is not installed")
    subprocess.run([executable, "--help"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
