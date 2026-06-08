from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"


def test_pip_install_exposes_pacman_command():
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    assert "[project.scripts]" in pyproject
    assert 'pacman = "pacman_apt.cli:main"' in pyproject
    assert 'pacman-apt = "pacman_apt.cli:main"' in pyproject


def test_setuptools_uses_src_package_layout():
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    assert "[tool.setuptools.packages.find]" in pyproject
    assert 'where = ["src"]' in pyproject
