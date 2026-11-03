# pacman-apt (A pacman-like CLI compatibility layer for linux systems)

## Abstract
`pacman-apt` provides a small subset of Arch Linux `pacman`-style commands on
linux system by translating them into native `apt-get` / `apt-cache` / `dpkg-query`
invocations. The goal is consistent operator muscle-memory across distributions,
not to replace the underlying package manager.

## Motivation
Operators and developers frequently work across multiple Linux distributions.
Command surface area differences (e.g. `pacman -Syu` vs `apt update && apt upgrade`)
increase cognitive load and can lead to mistakes during routine maintenance.

This project reduces that friction by offering a minimal, explicit translation layer.

## Scope
### Goals
- Provide a pacman-like UX for common workflows on linux system:
  - `-Syu`, `-S`, `-R`, `-Rns`, `-Ss`, `-Qi`, `-Q`
- Prefer stable, script-friendly Debian tooling (`apt-get`, `apt-cache`, `dpkg-query`)
- Transparent execution: print commands before running them

### Non-goals
- Not a package manager: no repository handling, no dependency resolution
- Not a full `pacman` implementation
- Not intended for Arch Linux (where `pacman` already exists)

## Design Overview
`pacman-apt` parses a small flag subset and maps it to linux tooling:

| pacman-style | linux backend |
|---|---|
| `pacman -Syu` | `apt-get update && apt-get dist-upgrade -y` |
| `pacman -S <pkg...>` | `apt-get install -y <pkg...>` |
| `pacman -R <pkg...>` | `apt-get remove -y <pkg...>` |
| `pacman -Rns <pkg...>` | `apt-get purge -y <pkg...> && apt-get autoremove --purge -y` |
| `pacman -Ss <query>` | `apt-cache search <query>` |
| `pacman -Qi <pkg>` | `apt-cache show <pkg>` (metadata; see Limitations) |
| `pacman -Q` | `dpkg-query -W -f='${binary:Package}\t${Version}\n'` |

For design rationale, see `docs/design.md`.

## Security Model
- No `shell=True`; all subprocess calls use explicit argument arrays
- Conservative privilege handling (uses `sudo` when not root)
- Commands are echoed before execution for auditability

See `docs/security.md` for the threat model and assumptions.

## Compatibility
- Debian: stable
- Ubuntu: LTS

(Exact versions may vary; see `docs/compatibility.md`.)

## Installation
### Install with pip
From a local checkout:
```bash
python -m pip install .
```

For development, use an editable install:
```bash
python -m pip install -e .
```

Both pip installs create one command in the active Python environment:
- `pacman-apt`

The pip package deliberately does not install a command named `pacman`, so it
cannot shadow a real `pacman` binary. For muscle memory on Debian/Ubuntu, opt in
with a shell alias:
```bash
alias pacman=pacman-apt
```

If your Python environment's script directory is not on `PATH`, run the module
entrypoint directly instead:
```bash
python -m pacman_apt.cli --help
```

### Manual (single-file)
```bash
sudo install -m 0755 pacman /usr/local/bin/pacman
```
