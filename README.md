# pacman-apt (A pacman-like CLI compatibility layer for linux systems)

## Abstract
`pacman-apt` provides a small subset of Arch Linux `pacman`-style commands on
Debian and Ubuntu by translating them into native `apt-get` / `apt-cache` /
`dpkg-query` invocations.

The goal is consistent operator muscle-memory across distributions, not to replace
the underlying package manager.

## Motivation
Operators and developers frequently work across multiple Linux distributions.
Command surface area differences, such as `pacman -Syu` versus
`apt-get update && apt-get dist-upgrade`, increase cognitive load and can lead
to mistakes during routine maintenance.

This project reduces that friction by offering a minimal, explicit translation layer.

## Scope

### Goals
- Provide a pacman-like UX for common workflows on Debian/Ubuntu:
  - `-Syu`
  - `-S`
  - `-R`
  - `-Rns`
  - `-Ss`
  - `-Qi`
  - `-Q`
- Prefer stable, script-friendly Debian tooling:
  - `apt-get`
  - `apt-cache`
  - `dpkg-query`
- Print commands before running them for transparency.

### Non-goals
- Not a package manager.
- No repository handling of its own.
- No dependency resolution of its own.
- Not a full `pacman` implementation.
- Not intended for Arch Linux, where the real `pacman` already exists.

## Command mapping

| pacman-style | Debian/Ubuntu backend |
|---|---|
| `pacman -Syu` | `apt-get update && apt-get dist-upgrade -y` |
| `pacman -S <pkg...>` | `apt-get install -y <pkg...>` |
| `pacman -R <pkg...>` | `apt-get remove -y <pkg...>` |
| `pacman -Rns <pkg...>` | `apt-get purge -y <pkg...> && apt-get autoremove --purge -y` |
| `pacman -Ss <query>` | `apt-cache search <query>` |
| `pacman -Qi <pkg>` | `apt-cache show <pkg>` |
| `pacman -Q` | `dpkg-query -W -f='\${binary:Package}\t\${Version}\n'` |

For design rationale, see [docs/design.md](docs/design.md).

## Usage

Both installed entrypoints provide the same wrapper:

```bash
pacman --help
pacman-apt --help
```

### Update package lists and upgrade the system

```bash
pacman -Syu
```

Equivalent backend operations:

```bash
sudo apt-get update
sudo apt-get dist-upgrade -y
```

### Install packages

Install one package:

```bash
pacman -S htop
```

Install multiple packages:

```bash
pacman -S htop curl git
```

Equivalent backend operation:

```bash
sudo apt-get install -y htop curl git
```

### Remove a package

```bash
pacman -R htop
```

Equivalent backend operation:

```bash
sudo apt-get remove -y htop
```

### Purge a package and autoremove unused dependencies

```bash
pacman -Rns htop
```

Equivalent backend operations:

```bash
sudo apt-get purge -y htop
sudo apt-get autoremove --purge -y
```

> **Warning:** `-Rns` performs a system-wide `apt-get autoremove --purge`
> after purging the requested package. Review what APT plans to remove when
> using this on important systems.

### Search available packages

```bash
pacman -Ss nginx
```

You can use multiple search terms:

```bash
pacman -Ss python development
```

Equivalent backend operation:

```bash
apt-cache search nginx
```

### Show package metadata

```bash
pacman -Qi nginx
```

Multiple package names are accepted:

```bash
pacman -Qi nginx curl
```

Equivalent backend operation:

```bash
apt-cache show nginx
```

> **Note:** Unlike Arch Linux `pacman -Qi`, the current wrapper uses
> `apt-cache show`. This displays package metadata and does not strictly mean
> that the package is installed.

### List installed packages

```bash
pacman -Q
```

Equivalent backend operation:

```bash
dpkg-query -W -f='${binary:Package}\t${Version}\n'
```

## Installation

### Recommended: pipx

On modern Debian/Ubuntu systems, system Python may be protected by PEP 668.
For a command-line application, `pipx` keeps the package in an isolated virtual
environment while exposing the CLI commands on your user `PATH`.

Install `pipx`:

```bash
sudo apt update
sudo apt install -y pipx
pipx ensurepath
```

Open a new shell, then install:

```bash
pipx install pacman-apt-wrapper
```

Verify:

```bash
pipx list
command -v pacman
command -v pacman-apt
pacman --help
```

A typical user installation exposes the commands under:

```text
~/.local/bin/pacman
~/.local/bin/pacman-apt
```

Upgrade later with:

```bash
pipx upgrade pacman-apt-wrapper
```

Uninstall with:

```bash
pipx uninstall pacman-apt-wrapper
```

### Install with pip in a virtual environment

From a local checkout:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

For development, use an editable install:

```bash
python -m pip install -e .
```

Both installs create these commands in the active Python environment:

- `pacman`
- `pacman-apt`

If the environment's script directory is not on `PATH`, run the module
entrypoint directly:

```bash
python -m pacman_apt.cli --help
```

### Manual single-file installation

If you are using the repository's standalone `pacman` script:

```bash
sudo install -m 0755 pacman /usr/local/bin/pacman
```

## Privilege behavior

Read-only operations such as search, package metadata, and installed-package
listing run without privilege escalation.

Operations that modify the system automatically use `sudo --` when the wrapper
is not already running as root.

Examples:

```bash
pacman -Ss nginx
pacman -Qi nginx
pacman -Q
```

may run without `sudo`, while:

```bash
pacman -Syu
pacman -S nginx
pacman -R nginx
pacman -Rns nginx
```

require root privileges and will invoke `sudo` when needed.

## Security Model
- No `shell=True`; subprocess calls use explicit argument arrays.
- Package names and search terms are passed as separate subprocess arguments.
- Conservative privilege handling uses `sudo` only for modifying operations.
- Commands are printed before execution for auditability.
- Unsupported flag combinations fail closed instead of being silently translated.

See [docs/security.md](docs/security.md) for the threat model and assumptions.

## Compatibility
- Debian
- Ubuntu

Requirements:

- `apt-get`
- `apt-cache`
- `dpkg-query`
- `sudo` for modifying operations when not already root

Exact versions may vary. See [docs/compatibility.md](docs/compatibility.md).

## Limitations

The wrapper intentionally implements only a small pacman-like command subset.

Unsupported pacman flags are rejected. Do not assume that a command supported by
Arch Linux `pacman` exists in this wrapper unless it is explicitly documented
above.
