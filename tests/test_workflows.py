from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_ci_matrix_mirrors_makefile_release_checks() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert 'python-version: ["3.11", "3.12", "3.13"]' in workflow
    assert "uv sync --locked --extra dev --extra torch" in workflow
    assert "--index-strategy unsafe-best-match" in workflow
    for target in ("build", "test-all", "format-check", "lint", "typecheck"):
        assert f"make {target}" in workflow


def test_release_uses_only_github_artifacts_and_smoke_checks_wheel() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "softprops/action-gh-release@v2" in workflow
    assert "scripts/check_package.py" in workflow
    assert "files: dist/*" in workflow
    assert "PYPI" not in workflow.upper()


def test_cpu_torch_source_is_explicit_and_locked() -> None:
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    cpu_index = "https://download.pytorch.org/whl/cpu"
    assert cpu_index in project and cpu_index in lock
    assert 'name = "nvidia-' not in lock
    assert 'name = "cuda-' not in lock
