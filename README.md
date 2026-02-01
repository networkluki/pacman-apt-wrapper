# pacman-apt (A pacman-like CLI compatibility layer for Debian/Ubuntu)

## Abstract
`pacman-apt` provides a small subset of Arch Linux `pacman`-style commands on
Debian/Ubuntu by translating them into native `apt-get` / `apt-cache` / `dpkg-query`
invocations. The goal is consistent operator muscle-memory across distributions,
not to replace the underlying package manager.

## Motivation
Operators and developers frequently work across multiple Linux distributions.
Command surface area differences (e.g. `pacman -Syu` vs `apt update && apt upgrade`)
increase cognitive load and can lead to mistakes during routine maintenance.

This project reduces that friction by offering a minimal, explicit translation layer.

## Scope
### Goals
- Provide a pacman-like UX for common workflows on Debian/Ubuntu:
  - `-Syu`, `-S`, `-R`, `-Rns`, `-Ss`, `-Qi`, `-Q`
- Prefer stable, script-friendly Debian tooling (`apt-get`, `apt-cache`, `dpkg-query`)
- Transparent execution: print commands before running them

### Non-goals
- Not a package manager: no repository handling, no dependency resolution
- Not a full `pacman` implementation
- Not intended for Arch Linux (where `pacman` already exists)

## Design Overview
`pacman-apt` parses a small flag subset and maps it to Debian tooling:

| pacman-style | Debian/Ubuntu backend |
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

## Usage
```bash
pacman -Ss nginx
pacman -Syu
pacman -S htop curl
pacman -Rns htop
pacman -Q
```
