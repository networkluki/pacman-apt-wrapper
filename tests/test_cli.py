from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pacman_apt.cli as cli  # noqa: E402


def test_split_args_separates_flags_and_args():
    flags, args = cli.split_args(["-Syu", "htop", "-R", "curl"])
    assert flags == ["-Syu", "-R"]
    assert args == ["htop", "curl"]


def test_has_flag_combined():
    assert cli.has_flag(["-Syu"], "S") is True
    assert cli.has_flag(["-Syu"], "y") is True
    assert cli.has_flag(["-Syu"], "u") is True
    assert cli.has_flag(["-Syu"], "R") is False


def test_main_help_prints_usage(monkeypatch, capsys):
    monkeypatch.setattr(cli, "ensure_tools", lambda: None)
    exit_code = cli.main(["--help"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "pacman (Debian/Ubuntu wrapper)" in captured.out


def test_main_search_requires_query(monkeypatch):
    monkeypatch.setattr(cli, "ensure_tools", lambda: None)
    errors = {}

    def fake_die(msg: str, code: int = 2) -> None:
        errors["msg"] = msg
        errors["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(cli, "die", fake_die)
    try:
        cli.main(["-Ss"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "Search requires a query" in errors["msg"]


def test_main_install_routes_to_apt_get(monkeypatch):
    monkeypatch.setattr(cli, "ensure_tools", lambda: None)
    monkeypatch.setattr(cli, "as_root", lambda cmd: cmd)
    called = {}

    def fake_run(cmd):
        called["cmd"] = cmd
        return 0

    monkeypatch.setattr(cli, "run", fake_run)
    exit_code = cli.main(["-S", "htop", "curl"])
    assert exit_code == 0
    assert called["cmd"] == ["apt-get", "install", "-y", "htop", "curl"]
