"""Install a built wheel in a temporary stdlib venv and smoke-check it."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
import venv
from pathlib import Path


def find_wheel(dist: Path) -> Path:
    """Choose the most recently built wheel from a distribution directory."""
    candidates = tuple(dist.glob("diurnix-*.whl"))
    if not candidates:
        raise FileNotFoundError(f"no diurnix wheel found in {dist}")
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def environment_python(root: Path) -> Path:
    """Return the conventional Python path for the current platform."""
    candidate = root / "bin" / "python"
    if candidate.exists():
        return candidate
    return root / "Scripts" / "python.exe"


def check_wheel(wheel: Path) -> None:
    """Install a wheel with pip and verify import plus console-module entry point."""
    with tempfile.TemporaryDirectory(prefix="diurnix-wheel-") as temporary:
        environment = Path(temporary) / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = environment_python(environment)
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)],
            check=True,
        )
        subprocess.run(
            [str(python), "-c", "import diurnix; print(diurnix.__version__)"], check=True
        )
        subprocess.run([str(python), "-m", "diurnix.cli", "--help"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    args = parser.parse_args()
    wheel = args.wheel if args.wheel is not None else find_wheel(args.dist)
    if not wheel.is_file():
        parser.error(f"wheel does not exist: {wheel}")
    check_wheel(wheel.resolve())
    print(f"checked {wheel.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
