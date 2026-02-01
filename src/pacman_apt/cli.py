#!/usr/bin/env python3
"""
pacman (Debian/Ubuntu wrapper)

Implements a small subset of pacman-style flags by translating to:
- apt-get (stable scripting)
- apt-cache (search/show)
- dpkg-query (installed list)

Supported:
  pacman -Syu
  pacman -S <pkg...>
  pacman -R <pkg...>
  pacman -Rns <pkg...>
  pacman -Ss <query...>
  pacman -Qi <pkg...>
  pacman -Q
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from typing import List, Tuple


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def ensure_tools() -> None:
    for tool in ("apt-get", "apt-cache", "dpkg-query"):
        if shutil.which(tool) is None:
            die(f"Required tool not found in PATH: {tool}")


def split_args(argv: List[str]) -> Tuple[List[str], List[str]]:
    flags: List[str] = []
    rest: List[str] = []
    for arg in argv:
        if arg.startswith("-") and len(arg) > 1:
            flags.append(arg)
        else:
            rest.append(arg)
    return flags, rest


def has_flag(flags: List[str], needle: str) -> bool:
    # Pacman combines flags like -Syu
    for flag in flags:
        if flag.startswith("--"):
            continue
        if needle in flag[1:]:
            return True
    return False


def as_root(cmd: List[str]) -> List[str]:
    # Auto-sudo for operations that modify the system
    if os.geteuid() == 0:
        return cmd
    if shutil.which("sudo") is None:
        die("This operation requires root, and sudo is not available.")
    return ["sudo", "--"] + cmd


def run(cmd: List[str]) -> int:
    print("+ " + " ".join(shlex.quote(c) for c in cmd))
    process = subprocess.run(cmd, check=False)
    return int(process.returncode)


def main(argv: List[str] | None = None) -> int:
    ensure_tools()

    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print(
            "pacman (Debian/Ubuntu wrapper)\n\n"
            "Examples:\n\n"
            "  pacman -Syu\n\n"
            "  pacman -S htop curl\n\n"
            "  pacman -R htop\n\n"
            "  pacman -Rns htop\n\n"
            "  pacman -Ss nginx\n\n"
            "  pacman -Qi nginx\n\n"
            "  pacman -Q\n"
        )
        return 0

    flags, args = split_args(argv)

    # pacman -Syu
    if has_flag(flags, "S") and has_flag(flags, "y") and has_flag(flags, "u"):
        cmds = [
            as_root(["apt-get", "update"]),
            as_root(["apt-get", "dist-upgrade", "-y"]),
        ]
        for cmd in cmds:
            rc = run(cmd)
            if rc != 0:
                return rc
        return 0

    # pacman -S <pkgs...>
    if has_flag(flags, "S") and args and not has_flag(flags, "u"):
        return run(as_root(["apt-get", "install", "-y"] + args))

    # pacman -R / -Rns <pkgs...>
    if has_flag(flags, "R") and args:
        purge = has_flag(flags, "n") and has_flag(flags, "s")
        if purge:
            # purge + autoremove --purge to mimic "remove + deps + config"
            rc = run(as_root(["apt-get", "purge", "-y"] + args))
            if rc != 0:
                return rc
            return run(as_root(["apt-get", "autoremove", "--purge", "-y"]))
        return run(as_root(["apt-get", "remove", "-y"] + args))

    # pacman -Ss <query...>
    if has_flag(flags, "Ss"):
        if not args:
            die("Search requires a query (e.g. pacman -Ss nginx)")
        return run(["apt-cache", "search"] + args)

    # pacman -Qi <pkg...>
    if has_flag(flags, "Qi"):
        if not args:
            die("Info requires package name(s) (e.g. pacman -Qi nginx)")
        # apt-cache show shows package metadata (not strictly installed-state)
        for pkg in args:
            rc = run(["apt-cache", "show", pkg])
            if rc != 0:
                return rc
        return 0

    # pacman -Q (list installed)
    if has_flag(flags, "Q") and not args:
        return run(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\\n"])

    die(f"Unsupported flags/args: flags={flags!r} args={args!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
