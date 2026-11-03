from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"


def test_pip_install_exposes_only_pacman_apt_command():
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    assert "[project.scripts]" in pyproject
    assert 'pacman-apt = "pacman_apt.cli:main"' in pyproject
    # A console script named "pacman" would shadow the real pacman on Arch.
    assert 'pacman = "' not in pyproject


def test_setuptools_uses_src_package_layout():
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    assert "[tool.setuptools.packages.find]" in pyproject
    assert 'where = ["src"]' in pyproject
