# Design

## Goals
- Provide a minimal pacman-like CLI surface for Debian/Ubuntu hosts.
- Translate a subset of pacman flags to stable `apt-get`, `apt-cache`, and `dpkg-query` commands.
- Favor explicit behavior and clear error messages.

## Non-goals
- Full pacman feature parity.
- Advanced dependency solving beyond what `apt-get` already provides.

## Supported Operations
- `-Syu`: `apt-get update` + `apt-get dist-upgrade -y`
- `-S <pkgs>`: `apt-get install -y <pkgs>`
- `-R <pkgs>`: `apt-get remove -y <pkgs>`
- `-Rns <pkgs>`: `apt-get purge -y <pkgs>` + `apt-get autoremove --purge -y`
- `-Ss <query>`: `apt-cache search <query>`
- `-Qi <pkgs>`: `apt-cache show <pkgs>`
- `-Q`: `dpkg-query -W -f=...`

## Error Handling
- Missing system tools produce immediate, actionable errors.
- Unsupported flags are rejected with a clear message.
